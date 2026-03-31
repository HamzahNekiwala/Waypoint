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
    def test_login_normalization(self):
        # Testing that "  User123  " becomes "user123"
        with app.app.test_request_context(method='POST', data={'username': '  User123  '}):
            response = app.login()
            # Checks if the redirect URL contains the lowercase, stripped name
            self.assertIn('user123', response.location)

    # UT-04-CB: Testing Cancellation logic
    @patch('app.load_data')
    @patch('app.save_data')
    def test_cancel_last_trip_logic(self, mock_save, mock_load):
        mock_load.return_value = {"guest": {"itinerary": [{"id": 1}]}}
        result = app.cancel_last_trip("guest")
        self.assertTrue(result)
        # Verify save_data was called with an empty list
        args, _ = mock_save.call_args
        self.assertEqual(len(args[1]["guest"]["itinerary"]), 0)

if __name__ == '__main__':
    unittest.main()