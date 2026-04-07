import unittest
import unittest.mock
import app


class TestCancellation(unittest.TestCase):
    def setUp(self):
        app.app.testing = True
        self.client = app.app.test_client()

    def test_cancel_route_removes_trip_with_context(self):
        users = {
            "trip_user": {
                "itinerary": [
                    {
                        "flight_id": "F1",
                        "hotel_id": "H1",
                        "destination": "Tokyo",
                        "date": "2026-07-05",
                        "flight_seat": "3A",
                        "hotel_room_id": "R1",
                        "attractions": [],
                    }
                ]
            }
        }
        catalog = {
            "flights": [
                {
                    "id": "F1",
                    "destination": "Tokyo",
                    "date": "2026-07-05",
                    "price": 100,
                    "seat_rows": 4,
                    "seat_letters": ["A", "B"],
                    "premium_rows": [1],
                    "premium_seat_fee": 20,
                    "blocked_seats": [],
                    "booked_seats": ["3A"],
                }
            ],
            "hotels": [
                {
                    "id": "H1",
                    "name": "Test Inn",
                    "city": "Tokyo",
                    "price": 50,
                    "available_dates": ["2026-07-05"],
                    "rooms": [
                        {
                            "id": "R1",
                            "floor": 2,
                            "type": "Standard",
                            "beds": "1 Queen",
                            "max_guests": 2,
                            "price_per_night": 50,
                            "available": False,
                        }
                    ],
                }
            ],
            "attractions": [],
        }

        with unittest.mock.patch("app.load_data") as load, unittest.mock.patch(
            "app.save_data"
        ) as save:

            def fake_load(name):
                if name == "users.json":
                    return users
                return catalog

            load.side_effect = fake_load
            resp = self.client.post("/cancel/trip_user/0", follow_redirects=False)
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(len(users["trip_user"]["itinerary"]), 0)
            self.assertNotIn("3A", catalog["flights"][0]["booked_seats"])
            self.assertTrue(catalog["hotels"][0]["rooms"][0]["available"])
            self.assertEqual(save.call_count, 2)


if __name__ == "__main__":
    unittest.main()
