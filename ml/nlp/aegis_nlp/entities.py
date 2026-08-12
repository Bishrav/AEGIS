from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractedEntity:
    type: str
    value: str
    confidence: float
    method: str


class HybridEntityExtractor:
    """Deterministic domain NER using gazetteers and conservative rules."""

    def __init__(self, gazetteers: dict[str, tuple[str, ...]] | None = None) -> None:
        self.gazetteers = gazetteers or {
            "DISTRICT": ("Sindhupalchok", "Kathmandu", "Kaski", "Chitwan"),
            "RIVER": ("Melamchi", "Bagmati", "Koshi", "Narayani", "Rapti"),
            "ROAD": ("Araniko Highway", "Prithvi Highway", "East-West Highway"),
        }

    def extract(self, text: str) -> list[ExtractedEntity]:
        entities: list[ExtractedEntity] = []
        for entity_type, values in self.gazetteers.items():
            for value in values:
                if re.search(rf"\b{re.escape(value)}\b", text, flags=re.IGNORECASE):
                    entities.append(ExtractedEntity(entity_type, value, 0.98, "gazetteer"))
        for match in re.finditer(r"\b(?:19|20)\d{2}[-/]\d{1,2}[-/]\d{1,2}\b", text):
            entities.append(ExtractedEntity("DATE", match.group(), 0.95, "regex"))
        return entities

