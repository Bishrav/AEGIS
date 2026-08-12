import unittest

from aegis_risk.audit import RiskAuditRecord
from aegis_risk.engine import RiskEngine


class RiskAuditTest(unittest.TestCase):
    def test_record_preserves_policy_and_components(self):
        result = RiskEngine().calculate({"river": 0.9, "source_confidence": 0.8})
        payload = RiskAuditRecord.from_result("incident-1", result).to_dict()

        self.assertEqual(payload["incident_id"], "incident-1")
        self.assertEqual(payload["policy_version"], "risk-v1")
        self.assertEqual(payload["components"]["river"], 0.9)
        self.assertTrue(payload["created_at"].endswith("+00:00"))


if __name__ == "__main__":
    unittest.main()
