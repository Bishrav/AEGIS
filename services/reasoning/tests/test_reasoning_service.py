import unittest

from aegis_reasoning.app import explain


class ReasoningServiceTest(unittest.TestCase):
    def test_explain_returns_citations(self):
        result = explain({
            "incident_summary": "High flood risk",
            "evidence": [{"evidence_id": "ev-0123456789abcdef", "document_id": "doc-1", "title": "Report", "snippet": "River levels rose.", "score": 0.8, "source_uri": "https://example.test/1"}],
        })
        self.assertEqual(result["evidence_ids"], ["ev-0123456789abcdef"])
        self.assertEqual(result["provider"], "MockLLMProvider")


if __name__ == "__main__":
    unittest.main()
