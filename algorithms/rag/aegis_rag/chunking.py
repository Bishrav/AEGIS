from __future__ import annotations

import hashlib

from .models import Document


def chunk_document(document: Document, max_words: int = 120, overlap: int = 20) -> list[dict[str, str]]:
    if max_words <= 0 or overlap < 0 or overlap >= max_words:
        raise ValueError("overlap must be non-negative and smaller than max_words")
    words = document.text.split()
    chunks: list[dict[str, str]] = []
    step = max_words - overlap
    for index, start in enumerate(range(0, len(words), step)):
        text = " ".join(words[start : start + max_words]).strip()
        if not text:
            continue
        digest = hashlib.sha256(f"{document.document_id}:{index}:{text}".encode()).hexdigest()[:16]
        chunks.append({
            "evidence_id": f"ev-{digest}",
            "document_id": document.document_id,
            "title": document.title,
            "text": text,
            "source_uri": document.source_uri,
        })
    return chunks
