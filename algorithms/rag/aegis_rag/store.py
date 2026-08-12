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


class PostgresEvidenceStore:
    """Supabase/Postgres pgvector persistence adapter."""

    def __init__(self, dsn: str, embedding_dimensions: int = 128) -> None:
        import psycopg

        self.connection = psycopg.connect(dsn, autocommit=True)
        self.embedding_dimensions = embedding_dimensions

    def upsert_document(self, document: Document, chunks: list[dict[str, str]], embeddings: list[list[float]] | None = None) -> None:
        if embeddings is not None and len(embeddings) != len(chunks):
            raise ValueError("one embedding is required per chunk")
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO aegis_documents (document_id, title, source_uri, source_type, published_at, content) VALUES (%s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (document_id) DO UPDATE SET title=EXCLUDED.title, source_uri=EXCLUDED.source_uri, content=EXCLUDED.content",
                (document.document_id, document.title, document.source_uri, document.source_type, document.published_at, document.text),
            )
            for index, chunk in enumerate(chunks):
                embedding = embeddings[index] if embeddings else None
                if embedding is not None and len(embedding) != self.embedding_dimensions:
                    raise ValueError("embedding dimension does not match store")
                vector = "[" + ",".join(str(float(value)) for value in embedding) + "]" if embedding else None
                cursor.execute(
                    "INSERT INTO aegis_evidence_chunks (evidence_id, document_id, title, content, source_uri, embedding) VALUES (%s, %s, %s, %s, %s, %s) "
                    "ON CONFLICT (evidence_id) DO UPDATE SET content=EXCLUDED.content, embedding=EXCLUDED.embedding",
                    (chunk["evidence_id"], document.document_id, document.title, chunk["text"], document.source_uri, vector),
                )

    def documents(self) -> list[Document]:
        raise NotImplementedError("use the document query API for persisted reads")

    def chunks(self) -> list[dict[str, str]]:
        raise NotImplementedError("use the retrieval query API for persisted reads")
