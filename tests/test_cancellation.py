import unittest
import app
import json
import os

#This is the "RED" test

class TestCancellation(unittest.TestCase):
    def setUp(self):
        #THIS CREATES A TEST USER THAT HAS ONE TRIP TO TEST WITH
        self.test_user = "test_guest"
        self.test_data = {
            self.test_user: {
                "itinerary": [
                    {"flight_id": "F-TYO-01", "hotel_id": "H-TYO-01", "destination": "Tokyo"}
                ]
            }
        }
        with open ('data/users.json', 'w') as f:
            json.dump(self.test_data, f)

    def test_cancel_trip_removes_from_json(self):
        #THIS IS TESTING A FEATURE THATS YET TO BE DEVELOPED!
        result = app.cancel_last_trip(self.test_user)
        self.assertTrue(result)

        with open('data/users.json', 'r') as f:
            updated_users = json.load(f)
        self.assertEqual(len(updated_users[self.test_user]['itinerary']), 0)

if __name__ == '__main__':
    unittest.main()