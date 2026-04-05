import unittest
import app

class TestWaypointSystem(unittest.TestCase):
    def setUp(self):
        app.app.testing = True
        self.client = app.app.test_client()

    # IT-03-CB: Multi-step routing logic
    def test_search_flow_redirection(self):
        # Simulate selecting a flight in a 'flight-first' flow
        response = self.client.post('/results/tester/Tokyo/flight/flight', data={
            'flight_id': 'F-TYO-01'
        }, follow_redirects=True)
        # Should now be showing the hotel selection page
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Choose Your Hotel', response.data)

    # ST-02-OB: Testing Itinerary History Toggle
    def test_itinerary_history_view(self):
        # Visiting itinerary with history=true
        response = self.client.get('/itinerary/tester?history=true')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Travel History', response.data)

    def test_admin_page_loads(self):
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Admin Dashboard', response.data)

    def test_cancel_route_redirects(self):
        response = self.client.post('/cancel/test_guest', follow_redirects=False)
        self.assertEqual(response.status_code, 302)

if __name__ == '__main__':
    unittest.main()