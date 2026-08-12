from __future__ import annotations

from typing import Any

from .engine import RiskEngine, RiskResult


def risk_for_incident(incident: Any, events: list[dict[str, Any]], engine: RiskEngine | None = None) -> RiskResult:
    event_types = {event["event_type"] for event in events if str(event["event_id"]) in incident.event_ids}
    rainfall = max((event.get("severity") or 0.0 for event in events if event["event_type"] == "HEAVY_RAIN"), default=0.0)
    river = max((event.get("severity") or 0.0 for event in events if event["event_type"] == "FLOOD"), default=0.0)
    infrastructure = 0.8 if "ROAD_CLOSURE" in event_types else 0.0
    agreement = min(len(event_types) / 3, 1.0)
    return (engine or RiskEngine()).calculate(
        {
            "rainfall": rainfall,
            "river": river,
            "forecast": 0.0,
            "infrastructure": infrastructure,
            "population": 0.0,
            "source_confidence": agreement,
        }
    )

