from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import IsolationForest


@dataclass(frozen=True)
class AnomalyResult:
    index: int
    value: float
    z_score: float
    statistical_score: float
    isolation_score: float
    anomaly_probability: float
    is_anomaly: bool


class AnomalyDetector:
    def __init__(self, z_threshold: float = 3.0, random_state: int = 42) -> None:
        self.z_threshold = z_threshold
        self.model = IsolationForest(contamination="auto", random_state=random_state)

    def fit_predict(self, values: list[float]) -> list[AnomalyResult]:
        data = np.asarray(values, dtype=float)
        mean = float(data.mean())
        std = float(data.std()) or 1.0
        z_scores = (data - mean) / std
        self.model.fit(data.reshape(-1, 1))
        raw = -self.model.score_samples(data.reshape(-1, 1))
        low, high = float(raw.min()), float(raw.max())
        isolation_scores = (raw - low) / ((high - low) or 1.0)
        results = []
        for index, value in enumerate(data):
            statistical = min(abs(float(z_scores[index])) / self.z_threshold, 1.0)
            probability = float((statistical + isolation_scores[index]) / 2)
            is_anomaly = abs(float(z_scores[index])) >= self.z_threshold or float(isolation_scores[index]) >= 0.8
            results.append(AnomalyResult(index, float(value), float(z_scores[index]), statistical, float(isolation_scores[index]), probability, is_anomaly))
        return results
