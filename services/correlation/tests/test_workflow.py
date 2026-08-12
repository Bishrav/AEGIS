import unittest

from aegis_correlation_service.app import add_note, correlate, list_incidents, update_status


class WorkflowTest(unittest.TestCase):
    def setUp(self):
        correlate({"incident_id": "workflow-1", "events": [{"event_id": "e1", "event_type": "HEAVY_RAIN", "occurred_at": "2026-08-12T09:00:00Z", "location": {"latitude": 27.7, "longitude": 85.3}, "entities": [{"type": "DISTRICT", "value": "Sindhupalchok"}], "severity": 0.9, "source_confidence": 0.9}]})

    def test_analyst_can_update_status_and_add_note(self):
        updated = update_status("workflow-1", {"status": "acknowledged"})
        noted = add_note("workflow-1", {"note": "Contacted district operations.", "author": "user-analyst"})
        self.assertEqual(updated["status"], "ACKNOWLEDGED")
        self.assertEqual(noted["notes"][-1]["author"], "user-analyst")
        self.assertTrue(any(item["incident_id"] == "workflow-1" for item in list_incidents()["incidents"]))


if __name__ == "__main__":
    unittest.main()
