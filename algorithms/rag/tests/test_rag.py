import unittest

from aegis_rag.chunking import chunk_document
from aegis_rag.models import Document
from aegis_rag.retrieval import HybridRetriever
from aegis_rag.evaluation import rank_by_mode, recall_at_k


class RagTest(unittest.TestCase):
    def setUp(self):
        documents = [
            Document("doc-flood", "Flood response", "Sindhupalchok flood response included river evacuation and road closure procedures.", "https://example.test/flood"),
            Document("doc-drought", "Drought response", "Drought preparedness focused on water storage and crop protection.", "https://example.test/drought"),
        ]
        self.retriever = HybridRetriever()
        for document in documents:
            self.retriever.add(chunk_document(document, max_words=80))

    def test_hybrid_retrieval_returns_citable_flood_evidence(self):
        package = self.retriever.retrieve("Sindhupalchok river flood road closure", top_k=1)
        self.assertEqual(package.hits[0].document_id, "doc-flood")
        self.assertTrue(package.hits[0].evidence_id.startswith("ev-"))
        self.assertEqual(package.evidence_ids, (package.hits[0].evidence_id,))

    def test_empty_top_k_is_safe(self):
        self.assertEqual(self.retriever.retrieve("flood", top_k=0).hits, ())

    def test_recall_and_mode_comparison_are_available(self):
        evaluation = recall_at_k(self.retriever, [("river flood response", {"doc-flood"})], top_k=5)
        self.assertEqual(evaluation.recall_at_k, 1.0)
        self.assertEqual(rank_by_mode(self.retriever, "river flood", "lexical", 1)[0].document_id, "doc-flood")
        self.assertEqual(rank_by_mode(self.retriever, "river flood", "semantic", 1)[0].document_id, "doc-flood")


if __name__ == "__main__":
    unittest.main()
