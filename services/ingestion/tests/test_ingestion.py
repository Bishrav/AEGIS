import unittest
from pathlib import Path

from aegis_ingestion.adapters import JsonReplayAdapter
from aegis_ingestion.models import RawRecord
from aegis_ingestion.normalize import EventNormalizer
from aegis_ingestion.ports import InMemoryEventPublisher, InMemoryRawPayloadStore, ingest_records


FIXTURES = Path(__file__).parents[1] / "fixtures"


class IngestionTests(unittest.TestCase):
    def test_replay_adapters_normalize_all_mvp_signal_types(self):
        expected = {
            "weather": "HEAVY_RAIN",
            "hydrology": "FLOOD",
            "infrastructure": "ROAD_CLOSURE",
            "report": "FLOOD",
        }
        for source_type, event_type in expected.items():
            path = FIXTURES / ("reports.json" if source_type == "report" else f"{source_type}.json")
            records = list(JsonReplayAdapter(source_type, path).read())
            event = EventNormalizer().normalize(records[0])
            self.assertEqual(event.event_type, event_type)
            self.assertEqual(event.schema_version, "event.v1")
            self.assertIsNotNone(event.location)

    def test_duplicate_record_is_not_published_twice(self):
        record = next(JsonReplayAdapter("weather", FIXTURES / "weather.json").read())
        raw_store = InMemoryRawPayloadStore()
        publisher = InMemoryEventPublisher()
        published = ingest_records([record, record], raw_store, publisher, EventNormalizer())
        self.assertEqual(published, 1)
        self.assertEqual(len(publisher.events), 1)

    def test_same_source_record_has_stable_event_id(self):
        record = next(JsonReplayAdapter("weather", FIXTURES / "weather.json").read())
        normalizer = EventNormalizer()
        self.assertEqual(normalizer.normalize(record).event_id, normalizer.normalize(record).event_id)

    def test_invalid_record_is_sent_to_dead_letter(self):
        record = RawRecord(
            source_id="fixture",
            source_type="weather",
            record_id="invalid",
            observed_at=next(JsonReplayAdapter("weather", FIXTURES / "weather.json").read()).observed_at,
            payload={"rainfall_mm": "not-a-number"},
        )
        publisher = InMemoryEventPublisher()
        ingest_records([record], InMemoryRawPayloadStore(), publisher, EventNormalizer())
        self.assertEqual(len(publisher.events), 0)
        self.assertEqual(len(publisher.dead_letters), 1)

    def test_published_event_contains_raw_object_uri(self):
        record = next(JsonReplayAdapter("weather", FIXTURES / "weather.json").read())
        publisher = InMemoryEventPublisher()
        ingest_records([record], InMemoryRawPayloadStore(), publisher, EventNormalizer())
        self.assertEqual(
            publisher.events[0].raw_object_uri,
            "memory://raw/fixture-weather-nepal/weather-sindhupalchok-2026-08-10T09:00:00Z.json",
        )


if __name__ == "__main__":
    unittest.main()
