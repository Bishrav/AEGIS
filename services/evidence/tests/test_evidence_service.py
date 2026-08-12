import unittest

from aegis_evidence_service.app import incident_evidence, ingest_document, search


class EvidenceServiceTest(unittest.TestCase):
    def test_document_ingestion_and_incident_search(self):
        result = ingest_document({"document_id": "phase5-doc", "title": "Flood bulletin", "text": "Sindhupalchok river flood response and road closure guidance.", "source_uri": "https://example.test/bulletin"})
        self.assertEqual(result["document_id"], "phase5-doc")
        evidence = incident_evidence("incident-1", "Sindhupalchok flood response", 3)
        self.assertIn(result["evidence_ids"][0], evidence["evidence_ids"])
        self.assertEqual(search("road closure", 1)["hits"][0]["document_id"], "phase5-doc")


if __name__ == "__main__":
    unittest.main()
