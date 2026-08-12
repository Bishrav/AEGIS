import unittest

from aegis_rag.models import EvidenceHit, EvidencePackage
from aegis_reasoning.explainer import EvidenceGroundedExplainer


class ExplainerTest(unittest.TestCase):
    def test_explanation_returns_internal_evidence_ids(self):
        evidence = EvidencePackage("flood", (EvidenceHit("ev-1", "doc-1", "Report", "River levels rose.", 0.8, "https://example.test/1"),))
        result = EvidenceGroundedExplainer().explain("High flood risk", evidence)
        self.assertEqual(result.evidence_ids, ("ev-1",))
        self.assertEqual(result.provider, "MockLLMProvider")

    def test_explanation_requires_evidence(self):
        with self.assertRaises(ValueError):
            EvidenceGroundedExplainer().explain("No evidence", EvidencePackage("query"))


if __name__ == "__main__":
    unittest.main()
