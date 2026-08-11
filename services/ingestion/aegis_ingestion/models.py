from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class RawRecord:
    source_id: str
    source_type: str
    record_id: str
    observed_at: datetime
    payload: dict[str, Any]


@dataclass(frozen=True)
class Entity:
    type: str
    value: str
    confidence: float = 1.0


@dataclass(frozen=True)
class Location:
    latitude: float
    longitude: float
    country: str | None = None
    district: str | None = None
    place_name: str | None = None


@dataclass(frozen=True)
class CanonicalEvent:
    event_id: UUID
    source_id: str
    event_type: str
    occurred_at: datetime
    observed_at: datetime
    source_confidence: float
    extraction_confidence: float
    schema_version: str = "event.v1"
    location: Location | None = None
    entities: tuple[Entity, ...] = field(default_factory=tuple)
    measurements: dict[str, float] = field(default_factory=dict)
    severity: float | None = None
    raw_object_uri: str | None = None

