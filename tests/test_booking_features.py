import copy
import unittest
import app


class TestBookingFeatures(unittest.TestCase):
    def _minimal_catalog(self):
        return {
            "flights": [
                {
                    "id": "F1",
                    "destination": "Tokyo",
                    "date": "2026-07-05",
                    "price": 100,
                    "seat_rows": 3,
                    "seat_letters": ["A", "B"],
                    "premium_rows": [1],
                    "premium_seat_fee": 25,
                    "blocked_seats": [],
                    "booked_seats": [],
                }
            ],
            "hotels": [
                {
                    "id": "H1",
                    "name": "Stay",
                    "city": "Tokyo",
                    "price": 80,
                    "available_dates": ["2026-07-05"],
                    "rooms": [
                        {
                            "id": "R1",
                            "floor": 1,
                            "type": "Queen",
                            "beds": "1 Queen",
                            "max_guests": 2,
                            "price_per_night": 90,
                            "available": True,
                        }
                    ],
                }
            ],
            "attractions": [
                {
                    "id": "A1",
                    "city": "Tokyo",
                    "name": "Museum",
                    "sessions": [
                        {
                            "id": "S1",
                            "start": "2026-07-05T10:00",
                            "end": "2026-07-05T11:00",
                            "price": 15,
                            "spots_left": 2,
                        }
                    ],
                }
            ],
        }

    def test_confirm_applies_premium_fee_and_attraction(self):
        catalog = self._minimal_catalog()
        users = {"u": {"itinerary": []}}
        cat = copy.deepcopy(catalog)
        ok = app.confirm_booking_direct(
            "u",
            "F1",
            "H1",
            "1A",
            "R1",
            [("A1", "S1")],
            catalog=cat,
            users=users,
        )
        self.assertTrue(ok)
        trip = users["u"]["itinerary"][0]
        self.assertEqual(trip["seat_surcharge"], 25)
        self.assertEqual(trip["hotel_room_price"], 90)
        self.assertEqual(trip["attractions_total"], 15)
        self.assertEqual(trip["total_price"], 100 + 25 + 90 + 15)
        self.assertIn("1A", cat["flights"][0]["booked_seats"])
        self.assertFalse(cat["hotels"][0]["rooms"][0]["available"])
        self.assertEqual(cat["attractions"][0]["sessions"][0]["spots_left"], 1)

    def test_validate_attraction_one_per_experience(self):
        catalog = self._minimal_catalog()
        catalog["attractions"][0]["sessions"].append(
            {
                "id": "S2",
                "start": "2026-07-05T14:00",
                "end": "2026-07-05T15:00",
                "price": 20,
                "spots_left": 2,
            }
        )
        ok, _ = app.validate_attraction_picks(
            catalog, "Tokyo", "2026-07-05", [("A1", "S1"), ("A1", "S2")]
        )
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main()
