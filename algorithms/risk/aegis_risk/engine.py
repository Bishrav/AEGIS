from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskResult:
    risk: float
    level: str
    components: dict[str, float]
    policy_version: str


class RiskEngine:
    def __init__(self, policy_version: str = "risk-v1") -> None:
        self.policy_version = policy_version
        self.weights = {
            "rainfall": 0.25,
            "river": 0.20,
            "forecast": 0.20,
            "infrastructure": 0.15,
            "population": 0.10,
            "source_confidence": 0.10,
        }

    def calculate(self, components: dict[str, float]) -> RiskResult:
        normalized = {name: min(max(float(components.get(name, 0.0)), 0.0), 1.0) for name in self.weights}
        score = min(sum(normalized[name] * weight for name, weight in self.weights.items()), 1.0)
        return RiskResult(score, _level(score), normalized, self.policy_version)


def _level(score: float) -> str:
    if score < 0.30:
        return "LOW"
    if score < 0.50:
        return "MODERATE"
    if score < 0.70:
        return "HIGH"
    return "CRITICAL"

