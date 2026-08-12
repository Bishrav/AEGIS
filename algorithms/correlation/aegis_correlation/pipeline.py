from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .incidents import CorrelatedIncident, IncidentAggregator
from aegis_risk.engine import RiskEngine, RiskResult
from aegis_risk.incident_policy import risk_for_incident


@dataclass(frozen=True)
class PipelineResult:
    incident: CorrelatedIncident
    risk: RiskResult


class IncidentPipeline:
    """Deterministic Phase 4 boundary from normalized events to risk."""

    def __init__(
        self,
        aggregator: IncidentAggregator | None = None,
        risk_engine: RiskEngine | None = None,
    ) -> None:
        self.aggregator = aggregator or IncidentAggregator()
        self.risk_engine = risk_engine or RiskEngine()

    def process(self, events: list[dict[str, Any]], incident_id: str) -> PipelineResult:
        incident = self.aggregator.group(events, incident_id)
        risk = risk_for_incident(incident, events, self.risk_engine)
        return PipelineResult(incident=incident, risk=risk)
