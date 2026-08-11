from __future__ import annotations

import hashlib
import re
from datetime import timedelta
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from .models import CanonicalEvent, Entity, Location, RawRecord


class EventNormalizer:
    """Convert source records into deterministic, versioned canonical events."""

    def normalize(self, record: RawRecord) -> CanonicalEvent:
        payload = record.payload
        location = _location(payload)
        event_type, extraction_confidence = _classify(record.source_type, payload)
        entities = tuple(_entities(payload, event_type))
        measurements = _measurements(payload)
        severity = _severity(event_type, measurements)

        return CanonicalEvent(
            event_id=uuid5(NAMESPACE_URL, f"aegis:event.v1:{record.source_id}:{record.record_id}"),
            source_id=record.source_id,
            event_type=event_type,
            occurred_at=record.observed_at,
            observed_at=record.observed_at,
            source_confidence=float(payload.get("source_confidence", 0.8)),
            extraction_confidence=extraction_confidence,
            location=location,
            entities=entities,
            measurements=measurements,
            severity=severity,
        )


def _location(payload: dict[str, Any]) -> Location | None:
    if "latitude" not in payload or "longitude" not in payload:
        return None
    return Location(
        latitude=float(payload["latitude"]),
        longitude=float(payload["longitude"]),
        country=payload.get("country", "Nepal"),
        district=payload.get("district"),
        place_name=payload.get("place_name"),
    )


def _classify(source_type: str, payload: dict[str, Any]) -> tuple[str, float]:
    explicit = payload.get("event_type")
    if explicit:
        return str(explicit), 1.0
    if source_type == "weather":
        return ("HEAVY_RAIN" if float(payload.get("rainfall_mm", 0)) >= 50 else "NORMAL", 1.0)
    if source_type == "hydrology":
        return ("FLOOD" if float(payload.get("river_level_m", 0)) >= float(payload.get("flood_threshold_m", 0)) else "NORMAL", 1.0)
    if source_type == "infrastructure":
        return ("ROAD_CLOSURE" if payload.get("status") == "closed" else "INFRASTRUCTURE_FAILURE", 1.0)
    if source_type == "report":
        text = str(payload.get("text", "")).lower()
        keywords = ("flood", "inundat", "overflow")
        return ("FLOOD" if any(word in text for word in keywords) else "NORMAL", 0.75)
    return "NORMAL", 0.5


def _entities(payload: dict[str, Any], event_type: str) -> list[Entity]:
    entities: list[Entity] = []
    if district := payload.get("district"):
        entities.append(Entity("DISTRICT", str(district)))
    if river := payload.get("river"):
        entities.append(Entity("RIVER", str(river)))
    if road := payload.get("road"):
        entities.append(Entity("ROAD", str(road)))
    if place := payload.get("place_name"):
        entities.append(Entity("LOCATION", str(place)))
    if event_type != "NORMAL":
        entities.append(Entity("INFRASTRUCTURE", event_type))
    return entities


def _measurements(payload: dict[str, Any]) -> dict[str, float]:
    keys = ("rainfall_mm", "temperature_c", "river_level_m", "discharge_m3s", "flood_threshold_m")
    return {key: float(payload[key]) for key in keys if key in payload}


def _severity(event_type: str, measurements: dict[str, float]) -> float | None:
    if event_type == "HEAVY_RAIN":
        return min(measurements.get("rainfall_mm", 0) / 200, 1.0)
    if event_type == "FLOOD":
        level = measurements.get("river_level_m", 0)
        threshold = measurements.get("flood_threshold_m", level or 1)
        return min(level / threshold, 1.0)
    if event_type == "ROAD_CLOSURE":
        return 0.7
    if event_type == "INFRASTRUCTURE_FAILURE":
        return 0.6
    return None


def deduplication_key(record: RawRecord) -> str:
    canonical_payload = repr(sorted(record.payload.items())).encode("utf-8")
    digest = hashlib.sha256(canonical_payload).hexdigest()
    return f"{record.source_id}:{record.record_id}:{digest}"

