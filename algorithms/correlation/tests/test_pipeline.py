import unittest

from aegis_correlation.pipeline import IncidentPipeline


class IncidentPipelineTest(unittest.TestCase):
    def test_replay_creates_incident_and_transparent_risk(self):
        events = [
            {
                "event_id": "rain-1",
                "event_type": "HEAVY_RAIN",
                "occurred_at": "2026-08-12T09:00:00Z",
                "location": {"latitude": 27.7, "longitude": 85.3},
                "entities": [{"type": "DISTRICT", "value": "Sindhupalchok"}],
                "severity": 0.9,
                "source_confidence": 0.95,
            },
            {
                "event_id": "river-1",
                "event_type": "FLOOD",
                "occurred_at": "2026-08-12T10:00:00Z",
                "location": {"latitude": 27.7, "longitude": 85.3},
                "entities": [{"type": "DISTRICT", "value": "Sindhupalchok"}],
                "severity": 0.85,
                "source_confidence": 0.9,
            },
            {
                "event_id": "road-1",
                "event_type": "ROAD_CLOSURE",
                "occurred_at": "2026-08-12T11:00:00Z",
                "location": {"latitude": 27.7, "longitude": 85.3},
                "entities": [{"type": "DISTRICT", "value": "Sindhupalchok"}],
                "severity": 0.8,
                "source_confidence": 0.85,
            },
        ]

        result = IncidentPipeline().process(events, "incident-sindhupalchok-1")

        self.assertEqual(result.incident.event_ids, ["rain-1", "river-1", "road-1"])
        self.assertEqual(result.risk.policy_version, "risk-v1")
        self.assertEqual(result.risk.level, "HIGH")
        self.assertIn("river", result.risk.components)


if __name__ == "__main__":
    unittest.main()
