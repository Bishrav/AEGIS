from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace

from .models import CanonicalEvent, RawRecord
from .normalize import deduplication_key


class InMemoryRawPayloadStore:
    def __init__(self) -> None:
        self.records: dict[str, RawRecord] = {}

    def put_if_absent(self, record: RawRecord) -> bool:
        key = deduplication_key(record)
        if key in self.records:
            return False
        self.records[key] = record
        return True

    def object_uri(self, record: RawRecord) -> str:
        return f"memory://raw/{record.source_id}/{record.record_id}.json"


class InMemoryEventPublisher:
    def __init__(self) -> None:
        self.events: list[CanonicalEvent] = []
        self.dead_letters: list[tuple[RawRecord, str]] = []

    def publish(self, event: CanonicalEvent) -> None:
        self.events.append(event)

    def dead_letter(self, record: RawRecord, reason: str) -> None:
        self.dead_letters.append((record, reason))


def ingest_records(
    records: Iterable[RawRecord],
    raw_store: InMemoryRawPayloadStore,
    publisher: InMemoryEventPublisher,
    normalizer,
) -> int:
    published = 0
    for record in records:
        if not raw_store.put_if_absent(record):
            continue
        try:
            event = normalizer.normalize(record)
            if hasattr(raw_store, "object_uri"):
                event = replace(event, raw_object_uri=raw_store.object_uri(record))
            publisher.publish(event)
            published += 1
        except (KeyError, TypeError, ValueError) as exc:
            publisher.dead_letter(record, str(exc))
    return published
