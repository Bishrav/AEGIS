from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import Any

from .models import CanonicalEvent


def canonical_event_to_dict(event: CanonicalEvent) -> dict[str, Any]:
    value = asdict(event)
    value["event_id"] = str(event.event_id)
    value["occurred_at"] = _timestamp(event.occurred_at)
    value["observed_at"] = _timestamp(event.observed_at)
    value["entities"] = [asdict(entity) for entity in event.entities]
    return value


def _timestamp(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def raw_record_to_dict(record) -> dict[str, Any]:
    return {
        "source_id": record.source_id,
        "source_type": record.source_type,
        "record_id": record.record_id,
        "observed_at": _timestamp(record.observed_at),
        "payload": record.payload,
    }

