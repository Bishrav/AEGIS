import json
import unittest
from pathlib import Path

from aegis_ingestion.adapters import JsonReplayAdapter
from aegis_ingestion.normalize import EventNormalizer
from aegis_ingestion.serialization import canonical_event_to_dict


class EventContractTests(unittest.TestCase):
    def test_normalized_fixture_matches_event_v1_shape(self):
        schema = json.loads(Path("schemas/events/canonical-event.schema.json").read_text(encoding="utf-8"))
        event = canonical_event_to_dict(
            EventNormalizer().normalize(
                next(JsonReplayAdapter("weather", Path("services/ingestion/fixtures/weather.json")).read())
            )
        )
        for field in schema["required"]:
            self.assertIn(field, event)
        self.assertEqual(event["schema_version"], "event.v1")
        self.assertIn(event["event_type"], schema["properties"]["event_type"]["enum"])
        self.assertGreaterEqual(event["source_confidence"], 0)
        self.assertLessEqual(event["source_confidence"], 1)

