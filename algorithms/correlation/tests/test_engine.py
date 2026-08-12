import unittest

from aegis_correlation.engine import CorrelationEngine


class CorrelationTests(unittest.TestCase):
    def test_heavy_rain_and_flood_correlate_with_cause_relationship(self):
        base = {"occurred_at": "2026-08-10T09:00:00Z", "location": {"latitude": 27.95, "longitude": 85.68}, "entities": [{"value": "Sindhupalchok"}], "source_confidence": 0.9}
        left = {**base, "event_id": "rain", "event_type": "HEAVY_RAIN"}
        right = {**base, "event_id": "flood", "event_type": "FLOOD", "occurred_at": "2026-08-10T10:15:00Z"}
        result = CorrelationEngine().compare(left, right)
        self.assertEqual(result.relationship, "CAUSES")
        self.assertGreater(result.correlation_score, 0.4)

