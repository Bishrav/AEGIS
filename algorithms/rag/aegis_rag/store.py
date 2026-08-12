from __future__ import annotations

from typing import Protocol

from .models import Document


class EvidenceStore(Protocol):
    def upsert_document(self, document: Document, chunks: list[dict[str, str]]) -> None: ...

    def documents(self) -> list[Document]: ...

    def chunks(self) -> list[dict[str, str]]: ...


class InMemoryEvidenceStore:
    def __init__(self) -> None:
        self._documents: dict[str, Document] = {}
        self._chunks: dict[str, dict[str, str]] = {}

    def upsert_document(self, document: Document, chunks: list[dict[str, str]]) -> None:
        self._documents[document.document_id] = document
        for chunk in chunks:
            self._chunks[chunk["evidence_id"]] = dict(chunk)

    def documents(self) -> list[Document]:
        return list(self._documents.values())

    def chunks(self) -> list[dict[str, str]]:
        return list(self._chunks.values())
