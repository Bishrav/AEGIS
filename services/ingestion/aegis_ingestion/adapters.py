from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Protocol

from .models import RawRecord


class SourceAdapter(Protocol):
    source_type: str

    def read(self) -> Iterable[RawRecord]:
        """Read raw records from a source without normalizing them."""


class JsonReplayAdapter:
    """Replay a frozen JSON fixture through the same adapter contract as live sources."""

    def __init__(self, source_type: str, path: Path) -> None:
        self.source_type = source_type
        self.path = path

    def read(self) -> Iterable[RawRecord]:
        document = json.loads(self.path.read_text(encoding="utf-8"))
        for item in document["records"]:
            yield RawRecord(
                source_id=item["source_id"],
                source_type=self.source_type,
                record_id=item["record_id"],
                observed_at=_parse_timestamp(item["observed_at"]),
                payload=item["payload"],
            )


def _parse_timestamp(value: str):
    from datetime import datetime

    return datetime.fromisoformat(value.replace("Z", "+00:00"))

