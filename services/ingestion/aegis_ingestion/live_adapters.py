from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .models import RawRecord


class OpenMeteoWeatherAdapter:
    source_type = "weather"

    def __init__(
        self,
        latitude: float,
        longitude: float,
        source_id: str = "open-meteo-weather",
        fetch_json: Callable[[str], dict] | None = None,
    ) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.source_id = source_id
        self.fetch_json = fetch_json or _fetch_json

    def read(self) -> Iterable[RawRecord]:
        query = urlencode(
            {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "hourly": "precipitation,temperature_2m",
                "forecast_days": 1,
                "timezone": "UTC",
            }
        )
        response = self.fetch_json(f"https://api.open-meteo.com/v1/forecast?{query}")
        hourly = response["hourly"]
        for timestamp, rainfall, temperature in zip(
            hourly["time"], hourly["precipitation"], hourly["temperature_2m"], strict=True
        ):
            observed_at = datetime.fromisoformat(timestamp).replace(tzinfo=UTC)
            yield RawRecord(
                source_id=self.source_id,
                source_type=self.source_type,
                record_id=f"{self.source_id}:{timestamp}",
                observed_at=observed_at,
                payload={
                    "rainfall_mm": rainfall,
                    "temperature_c": temperature,
                    "latitude": self.latitude,
                    "longitude": self.longitude,
                    "country": "Nepal",
                    "source_confidence": 0.85,
                },
            )


def _fetch_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "AEGIS/0.1 portfolio project"})
    with urlopen(request, timeout=20) as response:
        return json.load(response)
