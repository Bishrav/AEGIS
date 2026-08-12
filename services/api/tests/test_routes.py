import unittest

from aegis_api.app import incidents, ingest_evidence_document


class RouteTest(unittest.TestCase):
    def test_incident_route_is_exposed(self):
        self.assertTrue(callable(incidents))

    def test_evidence_ingestion_route_is_exposed(self):
        self.assertTrue(callable(ingest_evidence_document))


if __name__ == "__main__":
    unittest.main()
