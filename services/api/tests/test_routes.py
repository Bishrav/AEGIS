import unittest

from aegis_api.app import incidents


class RouteTest(unittest.TestCase):
    def test_incident_route_is_exposed(self):
        self.assertTrue(callable(incidents))


if __name__ == "__main__":
    unittest.main()
