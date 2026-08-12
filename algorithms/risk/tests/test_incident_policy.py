import unittest
from types import SimpleNamespace

from aegis_risk.incident_policy import risk_for_incident


class IncidentRiskTests(unittest.TestCase):
    def test_signal_chain_produces_transparent_risk_components(self):
        incident = SimpleNamespace(event_ids=["rain", "river", "road"])
        events = [
            {"event_id": "rain", "event_type": "HEAVY_RAIN", "severity": 0.8},
            {"event_id": "river", "event_type": "FLOOD", "severity": 1.0},
            {"event_id": "road", "event_type": "ROAD_CLOSURE", "severity": 0.7},
        ]
        result = risk_for_incident(incident, events)
        self.assertEqual(result.policy_version, "risk-v1")
        self.assertEqual(result.components["river"], 1.0)
        self.assertGreater(result.risk, 0.3)

