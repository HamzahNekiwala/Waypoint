from flask import Flask, render_template, json, request, redirect, url_for
import os

app = Flask(__name__)

def load_data(file_name):
    path = os.path.join('data', file_name)
    with open(path, 'r') as f:
        return json.load(f)

def save_data(file_name, data):
    path = os.path.join('data', file_name)
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)


def parse_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_csv(value):
    return [item.strip() for item in (value or '').split(',') if item.strip()]


def flight_is_available(flight):
    seats = flight.get('available_seats')
    return seats is None or seats > 0


def hotel_is_available(hotel, date=None):
    rooms = hotel.get('available_rooms')
    date_ok = date is None or date in hotel.get('available_dates', [])
    return date_ok and (rooms is None or rooms > 0)


def get_flights(catalog, destination=None, date=None):
    flights = catalog.get('flights', [])
    if destination:
        flights = [f for f in flights if f['destination'] == destination]
    if date:
        flights = [f for f in flights if f['date'] == date]
    return [f for f in flights if flight_is_available(f)]


def get_hotels(catalog, city=None, date=None):
    hotels = catalog.get('hotels', [])
    if city:
        hotels = [h for h in hotels if h['city'] == city]
    if date:
        hotels = [h for h in hotels if date in h.get('available_dates', [])]
    return [h for h in hotels if hotel_is_available(h, date)]


def adjust_availability(item, key, delta):
    if key in item and isinstance(item[key], int):
        item[key] = max(0, item[key] + delta)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username').lower().strip()
    return redirect(url_for('what_next', username=username))

@app.route('/next/<username>')
def what_next(username):
    return render_template('next.html', username=username)

@app.route('/book/<username>')
def book_home(username):
    catalog = load_data('catalog.json')
    return render_template('book.html', catalog=catalog, username=username)

@app.route('/search/<username>/<dest>')
def search_choice(username, dest):
    return render_template('choice.html', destination=dest, username=username)

@app.route('/results/<username>/<dest>/<flow>')
def show_results(username, dest, flow):
    catalog = load_data('catalog.json')
    flights = get_flights(catalog, destination=dest)
    hotels = get_hotels(catalog, city=dest)
    step = flow
    return render_template('results.html',
        username=username,
        destination=dest,
        flow=flow,
        step=step,
        flights=flights,
        hotels=hotels,
        prev_flight_id=None,
        prev_hotel_id=None
    )

@app.route('/results/<username>/<dest>/<flow>/<step>', methods=['POST'])
def show_results_step2(username, dest, flow, step):
    catalog = load_data('catalog.json')
    prev_flight_id = request.form.get('flight_id')
    prev_hotel_id = request.form.get('hotel_id')
    if prev_flight_id and prev_hotel_id:
        return confirm_booking_direct(username, prev_flight_id, prev_hotel_id)

    if step == 'hotel' and prev_flight_id:
        flight = next((f for f in catalog['flights'] if f['id'] == prev_flight_id), None)
        flights = get_flights(catalog, destination=dest)
        hotels = get_hotels(catalog, city=dest, date=flight['date'] if flight else None)
    elif step == 'flight' and prev_hotel_id:
        hotel = next((h for h in catalog['hotels'] if h['id'] == prev_hotel_id), None)
        hotel_dates = hotel.get('available_dates', []) if hotel else []
        flights = [f for f in get_flights(catalog, destination=dest) if f['date'] in hotel_dates]
        hotels = get_hotels(catalog, city=dest)
    else:
        flights = get_flights(catalog, destination=dest)
        hotels = get_hotels(catalog, city=dest)

    next_step = 'hotel' if flow == 'flight' else 'flight'
    return render_template('results.html',
        username=username,
        destination=dest,
        flow=flow,
        step=next_step,
        flights=flights,
        hotels=hotels,
        prev_flight_id=prev_flight_id,
        prev_hotel_id=prev_hotel_id
    )


def confirm_booking_direct(username, flight_id, hotel_id):
    users = load_data('users.json')
    catalog = load_data('catalog.json')
    flight = next(f for f in catalog['flights'] if f['id'] == flight_id)
    hotel = next(h for h in catalog['hotels'] if h['id'] == hotel_id)
    new_trip = {
        "flight_id": flight_id,
        "hotel_id": hotel_id,
        "destination": flight['destination'],
        "date": flight['date'],
        "total_price": flight['price'] + hotel['price']
    }
    if username not in users:
        users[username] = {"itinerary": []}
    users[username]['itinerary'].append(new_trip)

    adjust_availability(flight, 'available_seats', -1)
    adjust_availability(hotel, 'available_rooms', -1)

    save_data('users.json', users)
    save_data('catalog.json', catalog)
    return redirect(url_for('show_itinerary', username=username))


@app.route('/admin')
def admin_panel():
    catalog = load_data('catalog.json')
    return render_template('admin.html', catalog=catalog)


@app.route('/admin/manage', methods=['POST'])
def admin_manage():
    catalog = load_data('catalog.json')
    action = request.form.get('action')

    if action == 'add_flight':
        flight_id = request.form.get('flight_id', '').strip()
        destination = request.form.get('destination', '').strip()
        price = parse_int(request.form.get('price'))
        date = request.form.get('date', '').strip()
        seats = parse_int(request.form.get('available_seats'))

        if flight_id and destination and price is not None and date:
            new_flight = {
                'id': flight_id,
                'destination': destination,
                'price': price,
                'date': date
            }
            if seats is not None:
                new_flight['available_seats'] = seats
            catalog.setdefault('flights', []).append(new_flight)
            if destination not in catalog.setdefault('destinations', []):
                catalog['destinations'].append(destination)

    elif action == 'add_hotel':
        hotel_id = request.form.get('hotel_id', '').strip()
        name = request.form.get('name', '').strip()
        city = request.form.get('city', '').strip()
        price = parse_int(request.form.get('price'))
        available_dates = parse_csv(request.form.get('available_dates'))
        rooms = parse_int(request.form.get('available_rooms'))

        if hotel_id and name and city and price is not None and available_dates:
            new_hotel = {
                'id': hotel_id,
                'name': name,
                'city': city,
                'price': price,
                'available_dates': available_dates
            }
            if rooms is not None:
                new_hotel['available_rooms'] = rooms
            catalog.setdefault('hotels', []).append(new_hotel)
            if city not in catalog.setdefault('destinations', []):
                catalog['destinations'].append(city)

    elif action == 'update_item':
        item_type = request.form.get('item_type')
        item_id = request.form.get('item_id', '').strip()
        price = parse_int(request.form.get('price'))
        available_seats = parse_int(request.form.get('available_seats'))
        available_rooms = parse_int(request.form.get('available_rooms'))
        available_dates = parse_csv(request.form.get('available_dates'))

        item = None
        if item_type == 'flight':
            item = next((f for f in catalog.get('flights', []) if f['id'] == item_id), None)
        elif item_type == 'hotel':
            item = next((h for h in catalog.get('hotels', []) if h['id'] == item_id), None)

        if item:
            if price is not None:
                item['price'] = price
            if item_type == 'flight' and available_seats is not None:
                item['available_seats'] = available_seats
            if item_type == 'hotel':
                if available_rooms is not None:
                    item['available_rooms'] = available_rooms
                if available_dates:
                    item['available_dates'] = available_dates

    save_data('catalog.json', catalog)
    return redirect(url_for('admin_panel'))

@app.route('/confirm-booking/<username>', methods=['POST'])
def confirm_booking(username):
    flight_id = request.form.get('flight_id')
    hotel_id = request.form.get('hotel_id')
    return confirm_booking_direct(username, flight_id, hotel_id)

@app.route('/itinerary/<username>')
def show_itinerary(username):
    users = load_data('users.json')
    catalog = load_data('catalog.json')
    user_info = users.get(username, {"itinerary": []})
    itinerary = []

    for index, item in enumerate(user_info.get('itinerary', [])):
        hotel = next((h for h in catalog['hotels'] if h['id'] == item['hotel_id']), None)
        flight = next((f for f in catalog['flights'] if f['id'] == item['flight_id']), None)
        trip = item.copy()
        trip['hotel_name'] = hotel['name'] if hotel else "Hotel not found"
        trip['hotel_price'] = hotel['price'] if hotel else 0
        trip['flight_price'] = flight['price'] if flight else 0
        trip['trip_index'] = index
        itinerary.append(trip)
    show_history = request.args.get('history') == 'true'
    display_trips = itinerary if show_history else ([itinerary[-1]] if itinerary else [])
    return render_template('itinerary.html', username=username, bookings=display_trips, is_history=show_history)

@app.route('/cancel/<username>', methods=['POST'])
def cancel_last_trip(username):
    return cancel_booking(username, None)


@app.route('/cancel/<username>/<int:trip_index>', methods=['POST'])
def cancel_booking(username, trip_index=None):
    users = load_data('users.json')
    catalog = load_data('catalog.json')
    user_info = users.get(username)

    if not user_info or not user_info.get('itinerary'):
        return redirect(url_for('show_itinerary', username=username))

    if trip_index is None:
        trip_index = len(user_info['itinerary']) - 1

    if trip_index < 0 or trip_index >= len(user_info['itinerary']):
        return redirect(url_for('show_itinerary', username=username))

    trip = user_info['itinerary'].pop(trip_index)
    flight = next((f for f in catalog['flights'] if f['id'] == trip['flight_id']), None)
    hotel = next((h for h in catalog['hotels'] if h['id'] == trip['hotel_id']), None)

    if flight:
        adjust_availability(flight, 'available_seats', 1)
    if hotel:
        adjust_availability(hotel, 'available_rooms', 1)

    save_data('users.json', users)
    save_data('catalog.json', catalog)
    return redirect(url_for('show_itinerary', username=username))

if __name__ == '__main__':
    app.run(debug=True)