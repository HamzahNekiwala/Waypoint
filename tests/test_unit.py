# python -m unittest discover tests
# py -m unittest discover tests

import unittest
from unittest.mock import patch, mock_open
import app

class TestWaypointUnit(unittest.TestCase):

    # UT-01-CB & UT-02-CB: Testing Data I/O
    @patch('builtins.open', new_callable=mock_open, read_data='{"flights": [], "hotels": []}')
    def test_load_save_data(self, mock_file):
        # UT-01-CB
        result = app.load_data('catalog.json')
        self.assertEqual(result, {"flights": [], "hotels": []})
        
        # UT-02-CB
        app.save_data('test.json', {"key": "value"})
        self.assertTrue(mock_file.called)

    # UT-03-OB: Testing Login Logic
    @patch("app.load_data")
    def test_login_normalization(self, mock_load):
        # Testing that "  User123  " becomes "user123"
        users = {"user123": {"password": "123", "is_admin": False, "itinerary": []}}
        mock_load.return_value = users

        with app.app.test_request_context(method='POST', data={'username': '  User123  ', 'password': '123'}):
            response = app.handle_login()
            # Checks if the redirect URL contains the lowercase, stripped name
            self.assertIn('user123', response.location)

    # UT-04-CB: Cancellation removes last trip (via HTTP + mocked persistence)
    @patch("app.save_data")
    @patch("app.load_data")
    def test_cancel_last_trip_logic(self, mock_load, mock_save):
        users = {"guest": {"itinerary": [{"flight_id": "FX", "hotel_id": "HX", "attractions": []}]}}
        catalog = {
            "flights": [{"id": "FX", "booked_seats": []}],
            "hotels": [{"id": "HX", "rooms": []}],
            "attractions": [],
        }

        def fake_load(name):
            if name == "users.json":
                return users
            return catalog

        mock_load.side_effect = fake_load
        app.app.testing = True
        with app.app.test_client() as client:
            resp = client.post("/cancel/guest", follow_redirects=False)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(len(users["guest"]["itinerary"]), 0)
        self.assertTrue(mock_save.called)

if __name__ == '__main__':
    unittest.main()