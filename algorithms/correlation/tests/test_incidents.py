import unittest

from aegis_correlation.incidents import IncidentAggregator


class IncidentTests(unittest.TestCase):
    def test_flood_signal_chain_forms_one_incident(self):
        location = {"latitude": 27.95, "longitude": 85.68}
        events = [
            {"event_id": "rain", "event_type": "HEAVY_RAIN", "occurred_at": "2026-08-10T09:00:00Z", "location": location, "entities": [{"type": "DISTRICT", "value": "Sindhupalchok"}], "source_confidence": 0.9},
            {"event_id": "river", "event_type": "FLOOD", "occurred_at": "2026-08-10T10:15:00Z", "location": location, "entities": [{"type": "DISTRICT", "value": "Sindhupalchok"}], "source_confidence": 0.9},
            {"event_id": "road", "event_type": "ROAD_CLOSURE", "occurred_at": "2026-08-10T11:10:00Z", "location": location, "entities": [{"type": "DISTRICT", "value": "Sindhupalchok"}], "source_confidence": 0.9},
        ]
        incident = IncidentAggregator().group(events, "incident-1")
        self.assertEqual(incident.event_ids, ["rain", "river", "road"])
        self.assertEqual(incident.district, "Sindhupalchok")
        self.assertEqual(incident.event_types, {"HEAVY_RAIN", "FLOOD", "ROAD_CLOSURE"})

