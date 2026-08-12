from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


@dataclass(frozen=True)
class ForecastComparison:
    naive_mae: float
    naive_rmse: float
    seasonal_mae: float
    seasonal_rmse: float
    selected_model: str


def compare_baselines(values: list[float], horizon: int = 1, seasonal_period: int = 24) -> ForecastComparison:
    if len(values) <= max(horizon, seasonal_period):
        raise ValueError("forecast series is too short for requested baseline comparison")
    actual = np.asarray(values[-horizon:], dtype=float)
    naive = np.repeat(values[-horizon - 1], horizon)
    seasonal_source = values[-horizon - seasonal_period : -seasonal_period]
    seasonal = np.asarray(seasonal_source, dtype=float)
    if len(seasonal) != horizon:
        seasonal = np.repeat(values[-seasonal_period], horizon)
    naive_mae = float(mean_absolute_error(actual, naive))
    naive_rmse = float(mean_squared_error(actual, naive) ** 0.5)
    seasonal_mae = float(mean_absolute_error(actual, seasonal))
    seasonal_rmse = float(mean_squared_error(actual, seasonal) ** 0.5)
    selected = "seasonal" if seasonal_rmse < naive_rmse else "naive"
    return ForecastComparison(naive_mae, naive_rmse, seasonal_mae, seasonal_rmse, selected)

