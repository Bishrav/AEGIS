from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .engine import CorrelationEngine, CorrelationResult


@dataclass
class CorrelatedIncident:
    incident_id: str
    event_ids: list[str]
    correlations: list[CorrelationResult]
    district: str | None
    event_types: set[str] = field(default_factory=set)


class IncidentAggregator:
    def __init__(self, engine: CorrelationEngine | None = None, threshold: float = 0.35) -> None:
        self.engine = engine or CorrelationEngine()
        self.threshold = threshold

    def group(self, events: list[dict[str, Any]], incident_id: str) -> CorrelatedIncident:
        if not events:
            raise ValueError("cannot create an incident without events")
        correlations: list[CorrelationResult] = []
        included = {str(events[0]["event_id"])}
        for index, left in enumerate(events):
            for right in events[index + 1 :]:
                result = self.engine.compare(left, right)
                if result.correlation_score >= self.threshold:
                    correlations.append(result)
                    included.update((result.left_event_id, result.right_event_id))
        selected = [event for event in events if str(event["event_id"]) in included]
        districts = {
            entity["value"]
            for event in selected
            for entity in event.get("entities", [])
            if entity.get("type") == "DISTRICT"
        }
        return CorrelatedIncident(
            incident_id=incident_id,
            event_ids=[str(event["event_id"]) for event in selected],
            correlations=correlations,
            district=next(iter(districts), None),
            event_types={event["event_type"] for event in selected},
        )

