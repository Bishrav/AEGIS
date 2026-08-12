import unittest
from unittest.mock import patch

from fastapi import HTTPException

from aegis_evidence_service.app import incident_evidence, ingest_document, search


class EvidenceServiceTest(unittest.TestCase):
    def test_document_ingestion_and_incident_search(self):
        result = ingest_document({"document_id": "phase5-doc", "title": "Flood bulletin", "text": "Sindhupalchok river flood response and road closure guidance.", "source_uri": "https://example.test/bulletin"})
        self.assertEqual(result["document_id"], "phase5-doc")
        evidence = incident_evidence("incident-1", "Sindhupalchok flood response", 3)
        self.assertIn(result["evidence_ids"][0], evidence["evidence_ids"])
        self.assertEqual(search("road closure", 1)["hits"][0]["document_id"], "phase5-doc")

    def test_public_free_service_requires_internal_token_when_configured(self):
        with patch.dict("os.environ", {"AEGIS_SERVICE_TOKEN": "test-token"}):
            with self.assertRaises(HTTPException) as error:
                search("flood", 5, None)
        self.assertEqual(error.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
