"""One-off builder for data/catalog.json — run: python scripts/build_catalog.py"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def flight_template(fid, dest, date, price):
    return {
        "id": fid,
        "destination": dest,
        "date": date,
        "price": price,
        "aircraft": "Narrow-body",
        "seat_rows": 6,
        "seat_letters": ["A", "B", "C", "D"],
        "aisle_after": 2,
        "premium_rows": [1, 2],
        "premium_seat_fee": 45,
        "blocked_seats": ["1A", "6D"],
        "booked_seats": [],
    }


def make_rooms(prefix, base_prices):
    rooms = []
    types = [
        ("Standard Queen", "1 Queen", 2),
        ("Standard Twin", "2 Twin", 2),
        ("Deluxe King", "1 King", 2),
        ("Corner Studio", "1 King + Sofa", 3),
        ("Executive", "1 King", 2),
        ("Family", "2 Queen", 4),
    ]
    for floor in (5, 4, 3):
        for i, (rtype, beds, mx) in enumerate(types):
            rid = f"{prefix}-R{floor}{i + 1}"
            p = base_prices[i % len(base_prices)]
            rooms.append({
                "id": rid,
                "floor": floor,
                "type": rtype,
                "beds": beds,
                "max_guests": mx,
                "price_per_night": p,
                "available": True,
            })
    return rooms


def sessions_for_date(d, prefix, specs):
    out = []
    for i, (start_t, end_t, price, spots) in enumerate(specs):
        out.append({
            "id": f"{prefix}-{i + 1}",
            "start": f"{d}T{start_t}",
            "end": f"{d}T{end_t}",
            "price": price,
            "spots_left": spots,
        })
    return out


def main():
    destinations = ["Tokyo", "London", "Toronto", "Dubai", "Amsterdam"]

    flights = [
        flight_template("F-TYO-01", "Tokyo", "2026-07-05", 850),
        flight_template("F-TYO-02", "Tokyo", "2026-07-12", 920),
        flight_template("F-TYO-03", "Tokyo", "2026-07-19", 780),
        flight_template("F-LON-01", "London", "2026-06-12", 450),
        flight_template("F-LON-02", "London", "2026-06-18", 510),
        flight_template("F-LON-03", "London", "2026-06-25", 480),
        flight_template("F-YYZ-01", "Toronto", "2026-08-01", 300),
        flight_template("F-YYZ-02", "Toronto", "2026-08-08", 350),
        flight_template("F-YYZ-03", "Toronto", "2026-08-15", 320),
        flight_template("F-DXB-01", "Dubai", "2026-11-05", 1100),
        flight_template("F-DXB-02", "Dubai", "2026-11-12", 1250),
        flight_template("F-DXB-03", "Dubai", "2026-11-19", 980),
        flight_template("F-AMS-01", "Amsterdam", "2026-09-10", 600),
        flight_template("F-AMS-02", "Amsterdam", "2026-09-17", 650),
        flight_template("F-AMS-03", "Amsterdam", "2026-09-24", 580),
    ]

    hotels_data = [
        ("H-TYO-01", "Shibuya Sky Hotel", "Tokyo", [150, 145, 175, 210, 195, 165]),
        ("H-TYO-02", "Akihabara Inn", "Tokyo", [110, 105, 125, 140, 130, 115]),
        ("H-TYO-03", "Imperial Palace Suites", "Tokyo", [350, 340, 380, 420, 400, 360]),
        ("H-LON-01", "The Grand London", "London", [220, 215, 250, 280, 265, 235]),
        ("H-LON-02", "Piccadilly Lodge", "London", [140, 135, 155, 175, 165, 145]),
        ("H-LON-03", "Thames View B&B", "London", [180, 175, 200, 220, 210, 190]),
        ("H-YYZ-01", "CN Tower View Hotel", "Toronto", [210, 205, 230, 255, 240, 220]),
        ("H-YYZ-02", "Distillery District Lofts", "Toronto", [175, 170, 195, 215, 200, 185]),
        ("H-YYZ-03", "Lakefront Suites", "Toronto", [190, 185, 210, 230, 215, 200]),
        ("H-DXB-01", "Burj Al Arab Luxury", "Dubai", [850, 820, 900, 950, 920, 880]),
        ("H-DXB-02", "Desert Oasis Resort", "Dubai", [400, 390, 430, 460, 440, 410]),
        ("H-DXB-03", "Marina Sands Hotel", "Dubai", [300, 295, 320, 350, 330, 310]),
        ("H-AMS-01", "Canal Side Boutique", "Amsterdam", [250, 245, 275, 300, 285, 260]),
        ("H-AMS-02", "Dam Square Inn", "Amsterdam", [180, 175, 200, 220, 205, 190]),
        ("H-AMS-03", "The Windmill Suites", "Amsterdam", [220, 215, 240, 265, 250, 230]),
    ]

    date_map = {
        "Tokyo": ["2026-07-05", "2026-07-12", "2026-07-19"],
        "London": ["2026-06-12", "2026-06-18", "2026-06-25"],
        "Toronto": ["2026-08-01", "2026-08-08", "2026-08-15"],
        "Dubai": ["2026-11-05", "2026-11-12", "2026-11-19"],
        "Amsterdam": ["2026-09-10", "2026-09-17", "2026-09-24"],
    }

    hotels = []
    for hid, name, city, prices in hotels_data:
        rooms = make_rooms(hid, prices)
        min_p = min(r["price_per_night"] for r in rooms)
        hotels.append({
            "id": hid,
            "name": name,
            "city": city,
            "neighborhood": "City center",
            "star_rating": 4,
            "price": min_p,
            "available_dates": date_map[city],
            "rooms": rooms,
        })

    attractions = []
    tokyo_dates = [("2026-07-05", "a"), ("2026-07-12", "b"), ("2026-07-19", "c")]
    for d, suf in tokyo_dates:
        attractions.append({
            "id": f"ATR-TYO-MORI-{suf}",
            "city": "Tokyo",
            "name": "Mori Art Museum & Sky Deck",
            "description": "Timed entry with skyline views.",
            "sessions": sessions_for_date(d, f"S-TYO-M-{suf}", [
                ("10:00", "11:30", 32, 25),
                ("14:00", "15:30", 32, 25),
                ("17:00", "18:30", 38, 20),
            ]),
        })
        attractions.append({
            "id": f"ATR-TYO-TSUKI-{suf}",
            "city": "Tokyo",
            "name": "Tsukiji Outer Market Food Walk",
            "description": "Guided tasting tour.",
            "sessions": sessions_for_date(d, f"S-TYO-T-{suf}", [
                ("09:00", "11:00", 55, 18),
                ("12:30", "14:30", 55, 18),
            ]),
        })

    lon_dates = [("2026-06-12", "a"), ("2026-06-18", "b"), ("2026-06-25", "c")]
    for d, suf in lon_dates:
        attractions.append({
            "id": f"ATR-LON-TOWER-{suf}",
            "city": "London",
            "name": "Tower of London Highlights",
            "description": "Yeoman-led introduction and Crown Jewels slot.",
            "sessions": sessions_for_date(d, f"S-LON-TWR-{suf}", [
                ("09:30", "12:00", 48, 30),
                ("13:00", "15:30", 48, 28),
            ]),
        })
        attractions.append({
            "id": f"ATR-LON-THAMES-{suf}",
            "city": "London",
            "name": "Thames Evening Cruise",
            "description": "Sightseeing cruise with live commentary.",
            "sessions": sessions_for_date(d, f"S-LON-TH-{suf}", [
                ("18:00", "19:30", 42, 40),
                ("20:00", "21:30", 45, 35),
            ]),
        })

    yyz_dates = [("2026-08-01", "a"), ("2026-08-08", "b"), ("2026-08-15", "c")]
    for d, suf in yyz_dates:
        attractions.append({
            "id": f"ATR-YYZ-CN-{suf}",
            "city": "Toronto",
            "name": "CN Tower Observation",
            "description": "Glass floor experience and lookout.",
            "sessions": sessions_for_date(d, f"S-YYZ-CN-{suf}", [
                ("10:00", "11:00", 28, 50),
                ("15:00", "16:00", 28, 50),
                ("19:00", "20:00", 32, 40),
            ]),
        })
        attractions.append({
            "id": f"ATR-YYZ-AGO-{suf}",
            "city": "Toronto",
            "name": "AGO Curator Tour",
            "description": "Canadian masters focused walk-through.",
            "sessions": sessions_for_date(d, f"S-YYZ-AGO-{suf}", [
                ("11:00", "12:30", 22, 22),
                ("14:00", "15:30", 22, 22),
            ]),
        })

    dxb_dates = [("2026-11-05", "a"), ("2026-11-12", "b"), ("2026-11-19", "c")]
    for d, suf in dxb_dates:
        attractions.append({
            "id": f"ATR-DXB-DESERT-{suf}",
            "city": "Dubai",
            "name": "Desert Safari & Dinner",
            "description": "Dune drive, camp, and buffet.",
            "sessions": sessions_for_date(d, f"S-DXB-D-{suf}", [
                ("15:00", "21:00", 185, 12),
                ("15:30", "21:30", 185, 12),
            ]),
        })
        attractions.append({
            "id": f"ATR-DXB-FRAME-{suf}",
            "city": "Dubai",
            "name": "Dubai Frame Skywalk",
            "description": "Panoramic old and new city views.",
            "sessions": sessions_for_date(d, f"S-DXB-F-{suf}", [
                ("09:00", "10:30", 35, 60),
                ("16:00", "17:30", 35, 55),
            ]),
        })

    ams_dates = [("2026-09-10", "a"), ("2026-09-17", "b"), ("2026-09-24", "c")]
    for d, suf in ams_dates:
        attractions.append({
            "id": f"ATR-AMS-RJK-{suf}",
            "city": "Amsterdam",
            "name": "Rijksmuseum Highlights",
            "description": "Timed entry with audio guide.",
            "sessions": sessions_for_date(d, f"S-AMS-R-{suf}", [
                ("10:00", "12:30", 28, 35),
                ("13:30", "16:00", 28, 35),
            ]),
        })
        attractions.append({
            "id": f"ATR-AMS-CANAL-{suf}",
            "city": "Amsterdam",
            "name": "Canal Cruise Classic",
            "description": "Open boat route through central canals.",
            "sessions": sessions_for_date(d, f"S-AMS-C-{suf}", [
                ("11:00", "12:00", 18, 45),
                ("15:00", "16:00", 18, 45),
                ("18:00", "19:00", 22, 40),
            ]),
        })

    catalog = {
        "destinations": destinations,
        "flights": flights,
        "hotels": hotels,
        "attractions": attractions,
    }

    path = os.path.join(ROOT, "data", "catalog.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=4)
    print("Wrote", path)


if __name__ == "__main__":
    main()
