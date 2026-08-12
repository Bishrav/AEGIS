from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import exp
from typing import Any


@dataclass(frozen=True)
class CorrelationResult:
    left_event_id: str
    right_event_id: str
    temporal_score: float
    spatial_score: float
    entity_score: float
    relationship_score: float
    source_confidence: float
    correlation_score: float
    relationship: str


class CorrelationEngine:
    def __init__(self, temporal_weight: float = 0.3, spatial_weight: float = 0.25, entity_weight: float = 0.2, relationship_weight: float = 0.25) -> None:
        self.weights = (temporal_weight, spatial_weight, entity_weight, relationship_weight)

    def compare(self, left: dict[str, Any], right: dict[str, Any]) -> CorrelationResult:
        temporal = _temporal_score(left["occurred_at"], right["occurred_at"])
        spatial = _spatial_score(left.get("location"), right.get("location"))
        left_entities = {entity["value"].lower() for entity in left.get("entities", [])}
        right_entities = {entity["value"].lower() for entity in right.get("entities", [])}
        entity = len(left_entities & right_entities) / max(len(left_entities | right_entities), 1)
        relationship = _relationship(left["event_type"], right["event_type"])
        relationship_score = 1.0 if relationship else 0.0
        confidence = (left.get("source_confidence", 0.0) + right.get("source_confidence", 0.0)) / 2
        weights = self.weights
        score = temporal * weights[0] + spatial * weights[1] + entity * weights[2] + relationship_score * weights[3]
        return CorrelationResult(
            str(left["event_id"]), str(right["event_id"]), temporal, spatial, entity, relationship_score, confidence, score * confidence, relationship or "RELATED_TO"
        )


def _temporal_score(left: str | datetime, right: str | datetime) -> float:
    left_dt = _parse_time(left)
    right_dt = _parse_time(right)
    hours = abs((left_dt - right_dt).total_seconds()) / 3600
    return exp(-hours / 6)


def _spatial_score(left: dict[str, float] | None, right: dict[str, float] | None) -> float:
    if not left or not right:
        return 0.0
    distance = ((left["latitude"] - right["latitude"]) ** 2 + (left["longitude"] - right["longitude"]) ** 2) ** 0.5
    return max(0.0, 1.0 - distance / 0.5)


def _relationship(left_type: str, right_type: str) -> str | None:
    relationships = {
        ("HEAVY_RAIN", "FLOOD"): "CAUSES",
        ("FLOOD", "ROAD_CLOSURE"): "AFFECTS",
        ("HEAVY_RAIN", "ROAD_CLOSURE"): "CORRELATED_WITH",
    }
    return relationships.get((left_type, right_type)) or relationships.get((right_type, left_type))


def _parse_time(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

