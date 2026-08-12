import unittest

from aegis_rag.citations import extract_citations, validate_citations
from aegis_rag.models import Document, EvidencePackage
from aegis_rag.chunking import chunk_document
from aegis_rag.store import InMemoryEvidenceStore


class StoreCitationTest(unittest.TestCase):
    def test_store_upsert_is_idempotent_and_citations_are_validated(self):
        document = Document("doc-1", "Flood report", "River evacuation guidance.", "https://example.test/1")
        chunks = chunk_document(document)
        store = InMemoryEvidenceStore()
        store.upsert_document(document, chunks)
        store.upsert_document(document, chunks)
        self.assertEqual(len(store.documents()), 1)
        self.assertEqual(len(store.chunks()), 1)
        package = EvidencePackage("flood", ())
        self.assertEqual(extract_citations("See [ev-0123456789abcdef]."), ("ev-0123456789abcdef",))
        with self.assertRaises(ValueError):
            validate_citations(package, ("ev-0123456789abcdef",))


if __name__ == "__main__":
    unittest.main()
