from flask import Flask, render_template, json, request, redirect, url_for, abort
import os

app = Flask(__name__)

FLOW_FLIGHT_FIRST = ["flight", "seat", "hotel", "room", "attractions"]
FLOW_HOTEL_FIRST = ["hotel", "room", "flight", "seat", "attractions"]


def load_data(file_name):
    path = os.path.join("data", file_name)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(file_name, data):
    path = os.path.join("data", file_name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def parse_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parse_csv(value):
    return [item.strip() for item in (value or "").split(",") if item.strip()]


def flight_has_seat_map(flight):
    return bool(flight.get("seat_rows") and flight.get("seat_letters"))


def iter_seat_ids(flight):
    if not flight_has_seat_map(flight):
        return
    for row in range(1, int(flight["seat_rows"]) + 1):
        for letter in flight["seat_letters"]:
            yield f"{row}{letter}"


def parse_seat_row(seat_id):
    if not seat_id:
        return None
    i = 0
    while i < len(seat_id) and seat_id[i].isdigit():
        i += 1
    if i == 0:
        return None
    try:
        return int(seat_id[:i])
    except ValueError:
        return None


def seat_is_premium(flight, seat_id):
    row = parse_seat_row(seat_id)
    if row is None:
        return False
    return row in flight.get("premium_rows", [])


def seat_surcharge_for(flight, seat_id):
    if not seat_is_premium(flight, seat_id):
        return 0
    return int(flight.get("premium_seat_fee", 0))


def is_seat_free(flight, seat_id):
    if not seat_id or not flight_has_seat_map(flight):
        return False
    row = parse_seat_row(seat_id)
    letter = seat_id[len(str(row)) :] if row is not None else ""
    if row is None or row < 1 or row > flight["seat_rows"]:
        return False
    if letter not in flight["seat_letters"]:
        return False
    if seat_id in flight.get("blocked_seats", []):
        return False
    booked = flight.setdefault("booked_seats", [])
    if seat_id in booked:
        return False
    return True


def count_free_seats(flight):
    if flight_has_seat_map(flight):
        return sum(1 for sid in iter_seat_ids(flight) if is_seat_free(flight, sid))
    seats = flight.get("available_seats")
    if seats is None:
        return 10**9
    return max(0, seats)


def flight_is_available(flight):
    return count_free_seats(flight) > 0


def hotel_has_room_inventory(hotel):
    rooms = hotel.get("rooms")
    return bool(rooms)


def count_available_rooms(hotel, trip_date=None):
    rooms = hotel.get("rooms")
    if not rooms:
        r = hotel.get("available_rooms")
        if r is None:
            return 10**9
        return max(0, r)
    if trip_date and trip_date not in hotel.get("available_dates", []):
        return 0
    return sum(1 for r in rooms if r.get("available", True))


def hotel_is_available(hotel, date=None):
    date_ok = date is None or date in hotel.get("available_dates", [])
    if not date_ok:
        return False
    return count_available_rooms(hotel, date) > 0


def hotel_cheapest_room_price(hotel):
    rooms = hotel.get("rooms")
    if not rooms:
        return hotel.get("price", 0)
    avail = [r["price_per_night"] for r in rooms if r.get("available", True)]
    if not avail:
        return hotel.get("price", 0)
    return min(avail)


def get_flights(catalog, destination=None, date=None):
    flights = catalog.get("flights", [])
    if destination:
        flights = [f for f in flights if f["destination"] == destination]
    if date:
        flights = [f for f in flights if f["date"] == date]
    return [f for f in flights if flight_is_available(f)]


def get_hotels(catalog, city=None, date=None):
    hotels = catalog.get("hotels", [])
    if city:
        hotels = [h for h in hotels if h["city"] == city]
    if date:
        hotels = [h for h in hotels if date in h.get("available_dates", [])]
    return [h for h in hotels if hotel_is_available(h, date)]


def get_attractions_for_trip_date(catalog, city, trip_date):
    out = []
    for att in catalog.get("attractions", []):
        if att.get("city") != city:
            continue
        sessions = [
            s for s in att.get("sessions", [])
            if (s.get("start") or "").startswith(trip_date)
        ]
        if sessions:
            copy_att = {**att, "sessions": sessions}
            out.append(copy_att)
    return out


def find_flight(catalog, flight_id):
    return next((f for f in catalog.get("flights", []) if f["id"] == flight_id), None)


def find_hotel(catalog, hotel_id):
    return next((h for h in catalog.get("hotels", []) if h["id"] == hotel_id), None)


def find_hotel_room(hotel, room_id):
    if not hotel or not room_id:
        return None
    return next((r for r in hotel.get("rooms", []) if r["id"] == room_id), None)


def find_attraction_session(catalog, attraction_id, session_id):
    for att in catalog.get("attractions", []):
        if att["id"] != attraction_id:
            continue
        for sess in att.get("sessions", []):
            if sess["id"] == session_id:
                return att, sess
    return None, None


def rooms_grouped_by_floor(hotel):
    rooms = hotel.get("rooms") or []
    floors = sorted({r["floor"] for r in rooms}, reverse=True)
    return [(f, [r for r in rooms if r["floor"] == f]) for f in floors]


def build_seat_grid(flight):
    if not flight or not flight_has_seat_map(flight):
        return []
    aisle_after = flight.get("aisle_after")
    rows_out = []
    for r in range(1, int(flight["seat_rows"]) + 1):
        seats_out = []
        for idx, letter in enumerate(flight["seat_letters"]):
            sid = f"{r}{letter}"
            seats_out.append({
                "id": sid,
                "selectable": is_seat_free(flight, sid),
                "blocked": sid in flight.get("blocked_seats", []),
                "booked": sid in flight.get("booked_seats", []),
                "premium": r in flight.get("premium_rows", []),
                "aisle_after_here": aisle_after == idx + 1,
            })
        rows_out.append({"row_num": r, "seats": seats_out})
    return rows_out


def adjust_availability(item, key, delta):
    if key in item and isinstance(item[key], int):
        item[key] = max(0, item[key] + delta)


def flow_steps(flow):
    return FLOW_FLIGHT_FIRST if flow == "flight" else FLOW_HOTEL_FIRST


def next_step(flow, current_step):
    order = flow_steps(flow)
    try:
        i = order.index(current_step)
    except ValueError:
        return None
    if i + 1 < len(order):
        return order[i + 1]
    return None


def step_number(flow, step):
    try:
        return flow_steps(flow).index(step) + 1
    except ValueError:
        return 1


def read_accumulators(form):
    return {
        "flight_id": (form.get("acc_flight_id") or "").strip() or None,
        "flight_seat": (form.get("acc_flight_seat") or "").strip() or None,
        "hotel_id": (form.get("acc_hotel_id") or "").strip() or None,
        "hotel_room_id": (form.get("acc_hotel_room_id") or "").strip() or None,
    }


def parse_attr_picks(form):
    picks = []
    for raw in form.getlist("attr_pick"):
        if "|" not in raw:
            continue
        aid, sid = raw.split("|", 1)
        aid, sid = aid.strip(), sid.strip()
        if aid and sid:
            picks.append((aid, sid))
    return picks


def validate_attraction_picks(catalog, city, trip_date, picks):
    if not picks:
        return True, []
    resolved = []
    seen_attr = set()
    for aid, sid in picks:
        att, sess = find_attraction_session(catalog, aid, sid)
        if not att or not sess:
            return False, []
        if att.get("city") != city:
            return False, []
        if not (sess.get("start") or "").startswith(trip_date):
            return False, []
        if sess.get("spots_left", 0) < 1:
            return False, []
        if aid in seen_attr:
            return False, []
        seen_attr.add(aid)
        resolved.append((att, sess))
    return True, resolved


def confirm_booking_direct(
    username,
    flight_id,
    hotel_id,
    flight_seat,
    hotel_room_id,
    attraction_picks,
    catalog=None,
    users=None,
):
    """attraction_picks: list of (attraction_id, session_id). Persists if catalog/users None."""
    own_catalog = catalog is None
    own_users = users is None
    if own_catalog:
        catalog = load_data("catalog.json")
    if own_users:
        users = load_data("users.json")

    flight = find_flight(catalog, flight_id)
    hotel = find_hotel(catalog, hotel_id)
    if not flight or not hotel:
        if own_catalog and own_users:
            abort(400)
        return False

    trip_date = flight["date"]
    if trip_date not in hotel.get("available_dates", []):
        if own_catalog and own_users:
            abort(400)
        return False

    if flight_has_seat_map(flight):
        if not flight_seat or not is_seat_free(flight, flight_seat):
            if own_catalog and own_users:
                abort(400)
            return False
    else:
        flight_seat = flight_seat or "—"
        if not flight_is_available(flight):
            if own_catalog and own_users:
                abort(400)
            return False

    room = find_hotel_room(hotel, hotel_room_id)
    if hotel_has_room_inventory(hotel):
        if not room or not room.get("available", True):
            if own_catalog and own_users:
                abort(400)
            return False
    else:
        hotel_room_id = hotel_room_id or "—"
        if not hotel_is_available(hotel, trip_date):
            if own_catalog and own_users:
                abort(400)
            return False

    ok, resolved_attrs = validate_attraction_picks(
        catalog, flight["destination"], trip_date, attraction_picks
    )
    if not ok:
        if own_catalog and own_users:
            abort(400)
        return False

    seat_fee = seat_surcharge_for(flight, flight_seat) if flight_has_seat_map(flight) else 0
    room_price = (
        room["price_per_night"]
        if room
        else int(hotel.get("price", 0))
    )
    attr_total = sum(int(s["price"]) for _, s in resolved_attrs)
    total = int(flight["price"]) + seat_fee + room_price + attr_total

    attr_stored = []
    for att, sess in resolved_attrs:
        attr_stored.append({
            "attraction_id": att["id"],
            "session_id": sess["id"],
            "name": att["name"],
            "price": int(sess["price"]),
            "start": sess["start"],
            "end": sess["end"],
        })
        sess["spots_left"] = max(0, int(sess.get("spots_left", 0)) - 1)

    if flight_has_seat_map(flight):
        flight.setdefault("booked_seats", []).append(flight_seat)
    else:
        adjust_availability(flight, "available_seats", -1)

    if room:
        room["available"] = False
    else:
        adjust_availability(hotel, "available_rooms", -1)

    new_trip = {
        "flight_id": flight_id,
        "hotel_id": hotel_id,
        "destination": flight["destination"],
        "date": trip_date,
        "flight_seat": flight_seat,
        "hotel_room_id": hotel_room_id if room else None,
        "hotel_room_type": room["type"] if room else None,
        "hotel_room_beds": room["beds"] if room else None,
        "attractions": attr_stored,
        "flight_base_price": int(flight["price"]),
        "seat_surcharge": seat_fee,
        "hotel_room_price": room_price,
        "attractions_total": attr_total,
        "total_price": total,
    }

    if username not in users:
        users[username] = {"itinerary": []}
    users[username]["itinerary"].append(new_trip)

    if own_catalog:
        save_data("catalog.json", catalog)
    if own_users:
        save_data("users.json", users)
    return True


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username").lower().strip()
    return redirect(url_for("what_next", username=username))


@app.route("/next/<username>")
def what_next(username):
    return render_template("next.html", username=username)


@app.route("/book/<username>")
def book_home(username):
    catalog = load_data("catalog.json")
    return render_template("book.html", catalog=catalog, username=username)


@app.route("/search/<username>/<dest>")
def search_choice(username, dest):
    return render_template("choice.html", destination=dest, username=username)


def render_booking_step(
    username,
    dest,
    flow,
    step,
    catalog,
    acc,
    flights,
    hotels,
    seat_flight=None,
    room_hotel=None,
    attractions_list=None,
    error=None,
):
    total_steps = len(flow_steps(flow))
    seat_grid = build_seat_grid(seat_flight) if step == "seat" and seat_flight else []
    room_groups = (
        rooms_grouped_by_floor(room_hotel) if step == "room" and room_hotel else []
    )
    return render_template(
        "results.html",
        username=username,
        destination=dest,
        flow=flow,
        step=step,
        total_steps=total_steps,
        step_number=step_number(flow, step),
        flights=flights,
        hotels=hotels,
        acc_flight_id=acc.get("flight_id"),
        acc_flight_seat=acc.get("flight_seat"),
        acc_hotel_id=acc.get("hotel_id"),
        acc_hotel_room_id=acc.get("hotel_room_id"),
        seat_flight=seat_flight,
        room_hotel=room_hotel,
        seat_grid=seat_grid,
        room_groups=room_groups,
        attractions_list=attractions_list or [],
        premium_seat_fee=seat_flight.get("premium_seat_fee", 0) if seat_flight else 0,
        error=error,
    )


@app.route("/results/<username>/<dest>/<flow>")
def show_results(username, dest, flow):
    if flow not in ("flight", "hotel"):
        abort(404)
    catalog = load_data("catalog.json")
    first = "flight" if flow == "flight" else "hotel"
    acc = {
        "flight_id": None,
        "flight_seat": None,
        "hotel_id": None,
        "hotel_room_id": None,
    }
    flights = get_flights(catalog, destination=dest)
    hotels = get_hotels(catalog, city=dest)
    return render_booking_step(
        username, dest, flow, first, catalog, acc, flights, hotels
    )


@app.route("/results/<username>/<dest>/<flow>/<submitted_step>", methods=["POST"])
def booking_step_post(username, dest, flow, submitted_step):
    if flow not in ("flight", "hotel"):
        abort(404)
    catalog = load_data("catalog.json")
    acc = read_accumulators(request.form)
    order = flow_steps(flow)
    if submitted_step not in order:
        abort(404)

    error = None

    if submitted_step == "flight":
        fid = (request.form.get("flight_id") or "").strip()
        if not fid or not find_flight(catalog, fid):
            error = "Please select a flight."
        else:
            acc["flight_id"] = fid
            acc["flight_seat"] = None

    elif submitted_step == "seat":
        seat = (request.form.get("flight_seat") or "").strip()
        flight = find_flight(catalog, acc.get("flight_id"))
        if not flight or not seat or not is_seat_free(flight, seat):
            error = "Please select an available seat."
        else:
            acc["flight_seat"] = seat

    elif submitted_step == "hotel":
        hid = (request.form.get("hotel_id") or "").strip()
        flight = find_flight(catalog, acc.get("flight_id"))
        trip_date = flight["date"] if flight else None
        hotel = find_hotel(catalog, hid)
        if not hid or not hotel:
            error = "Please select a hotel."
        elif trip_date and trip_date not in hotel.get("available_dates", []):
            error = "That hotel is not available for your flight date."
        elif count_available_rooms(hotel, trip_date) < 1:
            error = "No rooms available at that hotel."
        else:
            acc["hotel_id"] = hid
            acc["hotel_room_id"] = None

    elif submitted_step == "room":
        rid = (request.form.get("hotel_room_id") or "").strip()
        hotel = find_hotel(catalog, acc.get("hotel_id"))
        room = find_hotel_room(hotel, rid) if hotel else None
        flight = find_flight(catalog, acc.get("flight_id"))
        trip_date = flight["date"] if flight else None
        if not rid or not room:
            error = "Please select a room."
        elif not room.get("available", True):
            error = "That room is no longer available."
        elif trip_date and trip_date not in (hotel or {}).get("available_dates", []):
            error = "Invalid dates for this stay."
        else:
            acc["hotel_room_id"] = rid

    elif submitted_step == "attractions":
        flight = find_flight(catalog, acc.get("flight_id"))
        hotel = find_hotel(catalog, acc.get("hotel_id"))
        if not flight or not hotel or not acc.get("flight_seat"):
            if flow == "flight":
                error = "Session expired. Start again from flight selection."
            else:
                error = "Session expired. Start again from hotel selection."
        elif hotel_has_room_inventory(hotel) and not acc.get("hotel_room_id"):
            error = "Please select a room first."
        elif not find_hotel_room(hotel, acc.get("hotel_room_id")) and hotel_has_room_inventory(
            hotel
        ):
            error = "Invalid room selection."
        else:
            picks = parse_attr_picks(request.form)
            ok, _ = validate_attraction_picks(
                catalog, dest, flight["date"], picks
            )
            if not ok:
                error = "One or more experiences are no longer available."
            else:
                confirm_booking_direct(
                    username,
                    acc["flight_id"],
                    acc["hotel_id"],
                    acc["flight_seat"],
                    acc["hotel_room_id"],
                    picks,
                )
                return redirect(url_for("show_itinerary", username=username))

    if error:
        flights = get_flights(catalog, destination=dest)
        hotels = get_hotels(catalog, city=dest)
        seat_flight = find_flight(catalog, acc.get("flight_id"))
        room_hotel = find_hotel(catalog, acc.get("hotel_id"))
        fl_err = find_flight(catalog, acc.get("flight_id"))
        trip_date = fl_err["date"] if fl_err else None
        attractions_list = (
            get_attractions_for_trip_date(catalog, dest, trip_date)
            if trip_date
            else []
        )
        return render_booking_step(
            username,
            dest,
            flow,
            submitted_step,
            catalog,
            acc,
            flights,
            hotels,
            seat_flight=seat_flight,
            room_hotel=room_hotel,
            attractions_list=attractions_list,
            error=error,
        )

    nxt = next_step(flow, submitted_step)
    if not nxt:
        abort(400)

    flights = get_flights(catalog, destination=dest)
    hotels = get_hotels(catalog, city=dest)
    seat_flight = find_flight(catalog, acc.get("flight_id"))
    room_hotel = find_hotel(catalog, acc.get("hotel_id"))

    if nxt == "hotel":
        trip_date = (seat_flight or {}).get("date")
        hotels = get_hotels(catalog, city=dest, date=trip_date)
    elif nxt == "flight":
        hotel = find_hotel(catalog, acc.get("hotel_id"))
        hotel_dates = hotel.get("available_dates", []) if hotel else []
        flights = [
            f
            for f in get_flights(catalog, destination=dest)
            if f["date"] in hotel_dates
        ]
    elif nxt == "room":
        room_hotel = find_hotel(catalog, acc.get("hotel_id"))
        hotels = [room_hotel] if room_hotel else []
    elif nxt == "seat":
        seat_flight = find_flight(catalog, acc.get("flight_id"))
    elif nxt == "attractions":
        trip_date = (find_flight(catalog, acc.get("flight_id")) or {}).get("date")
        attractions_list = get_attractions_for_trip_date(catalog, dest, trip_date)
        return render_booking_step(
            username,
            dest,
            flow,
            nxt,
            catalog,
            acc,
            flights,
            hotels,
            seat_flight=seat_flight,
            room_hotel=room_hotel,
            attractions_list=attractions_list,
        )

    return render_booking_step(
        username,
        dest,
        flow,
        nxt,
        catalog,
        acc,
        flights,
        hotels,
        seat_flight=seat_flight,
        room_hotel=room_hotel,
        attractions_list=[],
    )


@app.route("/admin")
def admin_panel():
    catalog = load_data("catalog.json")
    return render_template("admin.html", catalog=catalog)


@app.route("/admin/manage", methods=["POST"])
def admin_manage():
    catalog = load_data("catalog.json")
    action = request.form.get("action")

    if action == "add_flight":
        flight_id = request.form.get("flight_id", "").strip()
        destination = request.form.get("destination", "").strip()
        price = parse_int(request.form.get("price"))
        date = request.form.get("date", "").strip()
        seats = parse_int(request.form.get("available_seats"))

        if flight_id and destination and price is not None and date:
            new_flight = {
                "id": flight_id,
                "destination": destination,
                "price": price,
                "date": date,
                "aircraft": "Narrow-body",
                "seat_rows": 6,
                "seat_letters": ["A", "B", "C", "D"],
                "aisle_after": 2,
                "premium_rows": [1, 2],
                "premium_seat_fee": 45,
                "blocked_seats": ["1A", "6D"],
                "booked_seats": [],
            }
            if seats is not None:
                new_flight["available_seats"] = seats
            catalog.setdefault("flights", []).append(new_flight)
            if destination not in catalog.setdefault("destinations", []):
                catalog["destinations"].append(destination)

    elif action == "add_hotel":
        hotel_id = request.form.get("hotel_id", "").strip()
        name = request.form.get("name", "").strip()
        city = request.form.get("city", "").strip()
        price = parse_int(request.form.get("price"))
        available_dates = parse_csv(request.form.get("available_dates"))
        rooms_n = parse_int(request.form.get("available_rooms"))

        if hotel_id and name and city and price is not None and available_dates:
            rid = f"{hotel_id}-R501"
            new_hotel = {
                "id": hotel_id,
                "name": name,
                "city": city,
                "neighborhood": "City center",
                "star_rating": 3,
                "price": price,
                "available_dates": available_dates,
                "rooms": [
                    {
                        "id": rid,
                        "floor": 5,
                        "type": "Standard Queen",
                        "beds": "1 Queen",
                        "max_guests": 2,
                        "price_per_night": price,
                        "available": True,
                    }
                ],
            }
            if rooms_n is not None:
                new_hotel["available_rooms"] = rooms_n
            catalog.setdefault("hotels", []).append(new_hotel)
            if city not in catalog.setdefault("destinations", []):
                catalog["destinations"].append(city)

    elif action == "update_item":
        item_type = request.form.get("item_type")
        item_id = request.form.get("item_id", "").strip()
        price = parse_int(request.form.get("price"))
        available_seats = parse_int(request.form.get("available_seats"))
        available_rooms = parse_int(request.form.get("available_rooms"))
        available_dates = parse_csv(request.form.get("available_dates"))

        item = None
        if item_type == "flight":
            item = next(
                (f for f in catalog.get("flights", []) if f["id"] == item_id), None
            )
        elif item_type == "hotel":
            item = next(
                (h for h in catalog.get("hotels", []) if h["id"] == item_id), None
            )

        if item:
            if price is not None:
                item["price"] = price
            if item_type == "flight" and available_seats is not None:
                item["available_seats"] = available_seats
            if item_type == "hotel":
                if available_rooms is not None:
                    item["available_rooms"] = available_rooms
                if available_dates:
                    item["available_dates"] = available_dates

    save_data("catalog.json", catalog)
    return redirect(url_for("admin_panel"))


@app.route("/confirm-booking/<username>", methods=["POST"])
def confirm_booking(username):
    flight_id = request.form.get("flight_id")
    hotel_id = request.form.get("hotel_id")
    flight_seat = request.form.get("flight_seat")
    hotel_room_id = request.form.get("hotel_room_id")
    picks = parse_attr_picks(request.form)
    confirm_booking_direct(
        username, flight_id, hotel_id, flight_seat, hotel_room_id, picks
    )
    return redirect(url_for("show_itinerary", username=username))


@app.route("/itinerary/<username>")
def show_itinerary(username):
    users = load_data("users.json")
    catalog = load_data("catalog.json")
    user_info = users.get(username, {"itinerary": []})
    itinerary = []

    for index, item in enumerate(user_info.get("itinerary", [])):
        hotel = find_hotel(catalog, item.get("hotel_id"))
        flight = find_flight(catalog, item.get("flight_id"))
        trip = dict(item)
        trip["hotel_name"] = hotel["name"] if hotel else "Hotel not found"
        trip["hotel_price"] = item.get("hotel_room_price")
        if trip["hotel_price"] is None:
            trip["hotel_price"] = hotel["price"] if hotel else 0
        trip["flight_price"] = item.get("flight_base_price")
        if trip["flight_price"] is None:
            trip["flight_price"] = flight["price"] if flight else 0
        trip["trip_index"] = index
        trip.setdefault("flight_seat", "—")
        trip.setdefault("attractions", [])
        trip.setdefault("seat_surcharge", 0)
        itinerary.append(trip)
    show_history = request.args.get("history") == "true"
    display_trips = itinerary if show_history else ([itinerary[-1]] if itinerary else [])
    return render_template(
        "itinerary.html", username=username, bookings=display_trips, is_history=show_history
    )


@app.route("/cancel/<username>", methods=["POST"])
def cancel_last_trip(username):
    return cancel_booking(username, None)


@app.route("/cancel/<username>/<int:trip_index>", methods=["POST"])
def cancel_booking(username, trip_index=None):
    users = load_data("users.json")
    catalog = load_data("catalog.json")
    user_info = users.get(username)

    if not user_info or not user_info.get("itinerary"):
        return redirect(url_for("show_itinerary", username=username))

    if trip_index is None:
        trip_index = len(user_info["itinerary"]) - 1

    if trip_index < 0 or trip_index >= len(user_info["itinerary"]):
        return redirect(url_for("show_itinerary", username=username))

    trip = user_info["itinerary"].pop(trip_index)
    flight = find_flight(catalog, trip.get("flight_id"))
    hotel = find_hotel(catalog, trip.get("hotel_id"))

    if flight:
        seat = trip.get("flight_seat")
        if seat and seat != "—" and flight_has_seat_map(flight):
            booked = flight.setdefault("booked_seats", [])
            if seat in booked:
                booked.remove(seat)
        else:
            adjust_availability(flight, "available_seats", 1)

    if hotel:
        room = find_hotel_room(hotel, trip.get("hotel_room_id"))
        if room:
            room["available"] = True
        else:
            adjust_availability(hotel, "available_rooms", 1)

    for att_book in trip.get("attractions", []):
        _, sess = find_attraction_session(
            catalog, att_book.get("attraction_id"), att_book.get("session_id")
        )
        if sess:
            sess["spots_left"] = int(sess.get("spots_left", 0)) + 1

    save_data("users.json", users)
    save_data("catalog.json", catalog)
    return redirect(url_for("show_itinerary", username=username))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
