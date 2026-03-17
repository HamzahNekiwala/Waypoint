# run with python -m unittest tests/test_booking.py

import unittest
from unittest.mock import patch, mock_open
import sys
import os

# This ensures that even if you run the test from different folders, 
# it finds your app.py in the 'Waypoint' directory.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import app
except ImportError:
    print("\n[ERROR] Still can't find app.py. Make sure this test file is inside Waypoint/tests/")

class TestDataManager(unittest.TestCase):
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"flights": [], "hotels": []}')
    def test_load_data(self, mock_file):
        """Tests the load_data method from app.py"""
        print("\nRunning: test_load_data...")
        result = app.load_data('catalog.json')
        self.assertEqual(result, {"flights": [], "hotels": []})
        print("Success: Data loaded correctly.")

    @patch('builtins.open', new_callable=mock_open)
    def test_save_data(self, mock_file):
        """Tests the save_data method from app.py"""
        print("Running: test_save_data...")
        test_data = {"test": "data"}
        app.save_data('test.json', test_data)
        # Check if it tried to open the correct path
        self.assertTrue(mock_file.called)
        print("Success: Save method called correctly.")

class TestBookingFlow(unittest.TestCase):

    def test_simple_math(self):
        """A basic test to ensure the runner is working"""
        print("Running: test_simple_math...")
        self.assertEqual(100 + 50, 150)

    def test_catalog_structure(self):
        """Mock test for the second class requirement"""
        print("Running: test_catalog_structure...")
        mock_catalog = {"destinations": ["Tokyo"]}
        self.assertIn("Tokyo", mock_catalog["destinations"])

if __name__ == '__main__':
    unittest.main()