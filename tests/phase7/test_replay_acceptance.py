"""Deterministic replay and duplicate-delivery acceptance tests."""

from __future__ import annotations

import json
import unittest
from dataclasses import asdict
from pathlib import Path

from aegis_ingestion.adapters import JsonReplayAdapter
from aegis_ingestion.normalize import EventNormalizer
from aegis_ingestion.ports import InMemoryEventPublisher, InMemoryRawPayloadStore, ingest_records


FIXTURES = Path(__file__).parents[2] / "services" / "ingestion" / "fixtures"


def replay(source_type: str) -> list[str]:
    fixture = FIXTURES / ("reports.json" if source_type == "report" else f"{source_type}.json")
    normalizer = EventNormalizer()
    events = [normalizer.normalize(record) for record in JsonReplayAdapter(source_type, fixture).read()]
    return [json.dumps(asdict(event), default=str, sort_keys=True) for event in events]


class ReplayAcceptanceTests(unittest.TestCase):
    def test_all_mvp_replays_are_deterministic(self) -> None:
        for source_type in ("weather", "hydrology", "infrastructure", "report"):
            with self.subTest(source_type=source_type):
                self.assertEqual(replay(source_type), replay(source_type))

    def test_duplicate_delivery_across_batches_publishes_once(self) -> None:
        record = next(JsonReplayAdapter("weather", FIXTURES / "weather.json").read())
        store = InMemoryRawPayloadStore()
        publisher = InMemoryEventPublisher()
        normalizer = EventNormalizer()

        first = ingest_records([record], store, publisher, normalizer)
        second = ingest_records([record, record], store, publisher, normalizer)

        self.assertEqual(first, 1)
        self.assertEqual(second, 0)
        self.assertEqual(len(publisher.events), 1)

    def test_replay_event_ids_are_unique_within_each_source(self) -> None:
        for source_type in ("weather", "hydrology", "infrastructure", "report"):
            with self.subTest(source_type=source_type):
                event_ids = [item.split('"event_id": "', 1)[1].split('"', 1)[0] for item in replay(source_type)]
                self.assertEqual(len(event_ids), len(set(event_ids)))


if __name__ == "__main__":
    unittest.main()
