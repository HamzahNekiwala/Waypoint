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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username').lower().strip()
    return redirect(url_for('book_home', username=username))

@app.route('/itinerary/<username>')
def show_itinerary(username):
    users = load_data('users.json')
    catalog = load_data('catalog.json')
    user_info = users.get(username, {"itinerary": []})
    itinerary = user_info.get('itinerary', [])

    for item in itinerary:
        hotel = next((h for h in catalog['hotels'] if h['id'] == item['hotel_id']), None)
        item['hotel_name'] = hotel['name'] if hotel else "Hotel not found"

    # Toggle history via URL parameter ?history=true
    show_history = request.args.get('history') == 'true'
    display_trips = itinerary if show_history else ([itinerary[-1]] if itinerary else [])

    return render_template('itinerary.html', username=username, bookings=display_trips, is_history=show_history)

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
    flights = [f for f in catalog['flights'] if f['destination'] == dest]
    hotels = [h for h in catalog['hotels'] if h['city'] == dest]
    return render_template('results.html', username=username, destination=dest, flights=flights, hotels=hotels, flow=flow)

@app.route('/confirm-booking/<username>', methods=['POST'])
def confirm_booking(username):
    flight_id = request.form.get('flight_id')
    hotel_id = request.form.get('hotel_id')
    users = load_data('users.json')
    catalog = load_data('catalog.json')

    flight = next(f for f in catalog['flights'] if f['id'] == flight_id)
    hotel = next(h for h in catalog['hotels'] if h['id'] == hotel_id)

    new_trip = {
        "flight_id": flight_id, "hotel_id": hotel_id, "destination": flight['destination'],
        "date": flight['date'], "total_price": flight['price'] + hotel['price']
    }

    if username not in users: users[username] = {"itinerary": []}
    users[username]['itinerary'].append(new_trip)
    save_data('users.json', users)
    return redirect(url_for('show_itinerary', username=username))

if __name__ == '__main__':
    app.run(debug=True)