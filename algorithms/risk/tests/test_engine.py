import unittest

from aegis_risk.engine import RiskEngine


class RiskTests(unittest.TestCase):
    def test_risk_is_deterministic_and_exposes_components(self):
        components = {"rainfall": 0.91, "river": 0.87, "forecast": 0.79, "infrastructure": 0.75, "population": 0.68, "source_confidence": 0.94}
        engine = RiskEngine()
        first = engine.calculate(components)
        second = engine.calculate(components)
        self.assertEqual(first, second)
        self.assertEqual(first.level, "CRITICAL")
        self.assertEqual(first.policy_version, "risk-v1")

    def test_threshold_boundaries(self):
        engine = RiskEngine()
        self.assertEqual(engine.calculate({}).level, "LOW")
        self.assertEqual(engine.calculate({"rainfall": 1, "river": 1, "forecast": 1, "infrastructure": 1, "population": 1, "source_confidence": 1}).level, "CRITICAL")
