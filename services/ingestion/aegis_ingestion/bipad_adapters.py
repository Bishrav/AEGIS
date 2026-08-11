from __future__ import annotations

import json
from collections.abc import Callable, Iterable
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .models import RawRecord


class BipadAdapter:
    def __init__(
        self,
        resource: str,
        source_type: str,
        query: dict[str, str] | None = None,
        fetch_json: Callable[[str], dict] | None = None,
    ) -> None:
        self.resource = resource
        self.source_type = source_type
        self.query = query or {"limit": "25"}
        self.fetch_json = fetch_json or _fetch_json

    def read(self) -> Iterable[RawRecord]:
        url = f"https://bipadportal.gov.np/api/v1/{self.resource}/?{urlencode(self.query)}"
        response = self.fetch_json(url)
        for item in response.get("results", []):
            yield self._to_record(item)

    def _to_record(self, item: dict) -> RawRecord:
        raise NotImplementedError


class BipadRiverAdapter(BipadAdapter):
    def __init__(self, query: dict[str, str] | None = None, fetch_json=None) -> None:
        super().__init__("river", "hydrology", query, fetch_json)

    def _to_record(self, item: dict) -> RawRecord:
        coordinates = item.get("point", {}).get("coordinates", [None, None])
        observed_at = _parse_timestamp(item.get("waterLevelOn") or item["modifiedOn"])
        water_level = item.get("waterLevel")
        danger_level = item.get("dangerLevel")
        measurements = {}
        if water_level is not None:
            measurements["river_level_m"] = water_level
        if danger_level is not None:
            measurements["flood_threshold_m"] = danger_level
        return RawRecord(
            source_id="bipad-river",
            source_type="hydrology",
            record_id=f"bipad-river:{item['id']}:{item.get('waterLevelOn', item['modifiedOn'])}",
            observed_at=observed_at,
            payload={
                "river": item.get("title"),
                **measurements,
                "event_type": "FLOOD" if water_level is not None and danger_level is not None and water_level >= danger_level else "NORMAL",
                "latitude": coordinates[1],
                "longitude": coordinates[0],
                "source_confidence": 0.95,
                "status": item.get("status"),
                "basin": item.get("basin"),
            },
        )


class BipadIncidentAdapter(BipadAdapter):
    def __init__(self, source_type: str, query: dict[str, str] | None = None, fetch_json=None) -> None:
        super().__init__("incident", source_type, query, fetch_json)

    def _to_record(self, item: dict) -> RawRecord:
        coordinates = item.get("point", {}).get("coordinates", [None, None])
        title = item.get("title") or ""
        description = item.get("description") or item.get("detail") or ""
        text = f"{title}. {description}".strip()
        road_signal = any(word in text.lower() for word in ("road", "highway", "bridge", "landslide", "blocked"))
        source_type = self.source_type
        status = "closed" if source_type == "infrastructure" and road_signal else "reported"
        observed_at = _parse_timestamp(item.get("reportedOn") or item["modifiedOn"])
        return RawRecord(
            source_id="bipad-incident",
            source_type=source_type,
            record_id=f"bipad-incident:{item['id']}:{item.get('reportedOn', item['modifiedOn'])}",
            observed_at=observed_at,
            payload={
                "text": text,
                "event_type": "ROAD_CLOSURE" if status == "closed" else None,
                "status": status,
                "latitude": coordinates[1],
                "longitude": coordinates[0],
                "source_confidence": 0.9 if item.get("verified") else 0.75,
                "street_address": item.get("streetAddress"),
            },
        )


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _fetch_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "AEGIS/0.1 portfolio project"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)
