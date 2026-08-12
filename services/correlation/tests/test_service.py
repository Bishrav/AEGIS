import unittest

from aegis_correlation_service.app import correlate, get_incident


class CorrelationServiceTest(unittest.TestCase):
    def test_correlate_persists_replay_result(self):
        payload = {
            "incident_id": "incident-service-1",
            "events": [
                {"event_id": "rain", "event_type": "HEAVY_RAIN", "occurred_at": "2026-08-12T09:00:00Z", "location": {"latitude": 27.7, "longitude": 85.3}, "entities": [{"type": "DISTRICT", "value": "Sindhupalchok"}], "severity": 0.9, "source_confidence": 0.9},
                {"event_id": "river", "event_type": "FLOOD", "occurred_at": "2026-08-12T10:00:00Z", "location": {"latitude": 27.7, "longitude": 85.3}, "entities": [{"type": "DISTRICT", "value": "Sindhupalchok"}], "severity": 0.8, "source_confidence": 0.9},
                {"event_id": "road", "event_type": "ROAD_CLOSURE", "occurred_at": "2026-08-12T11:00:00Z", "location": {"latitude": 27.7, "longitude": 85.3}, "entities": [{"type": "DISTRICT", "value": "Sindhupalchok"}], "severity": 0.8, "source_confidence": 0.9},
            ],
        }
        result = correlate(payload)
        self.assertEqual(result["incident_id"], "incident-service-1")
        self.assertEqual(get_incident("incident-service-1")["risk"]["policy_version"], "risk-v1")
        self.assertIn("components", result["audit"])


if __name__ == "__main__":
    unittest.main()
