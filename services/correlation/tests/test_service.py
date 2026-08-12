import unittest
import json
from datetime import datetime
from pathlib import Path

from aegis_correlation_service.app import correlate, get_incident
from aegis_ingestion.models import RawRecord
from aegis_ingestion.normalize import EventNormalizer
from aegis_ingestion.serialization import canonical_event_to_dict


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

    def test_four_source_fixtures_replay_to_one_incident(self):
        fixture_dir = Path(__file__).parents[2] / "ingestion" / "fixtures"
        events = []
        for source_type, filename in (("weather", "weather.json"), ("hydrology", "hydrology.json"), ("infrastructure", "infrastructure.json"), ("report", "reports.json")):
            record = json.loads((fixture_dir / filename).read_text())["records"][0]
            canonical = EventNormalizer().normalize(RawRecord(
                source_id=record["source_id"],
                source_type=source_type,
                record_id=record["record_id"],
                observed_at=datetime.fromisoformat(record["observed_at"].replace("Z", "+00:00")),
                payload=record["payload"],
            ))
            events.append(canonical_event_to_dict(canonical))

        result = correlate({"incident_id": "incident-four-source", "events": events})

        self.assertEqual(result["event_ids"], [str(events[0]["event_id"]), str(events[1]["event_id"]), str(events[2]["event_id"]), str(events[3]["event_id"])])
        self.assertEqual(result["district"], "Sindhupalchok")
        self.assertEqual(result["risk"]["policy_version"], "risk-v1")


if __name__ == "__main__":
    unittest.main()
