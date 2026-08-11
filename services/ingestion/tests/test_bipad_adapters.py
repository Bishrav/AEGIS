import unittest

from aegis_ingestion.bipad_adapters import BipadIncidentAdapter, BipadRiverAdapter


class BipadAdapterTests(unittest.TestCase):
    def test_river_record_maps_level_threshold_and_coordinates(self):
        response = {
            "results": [{
                "id": 42,
                "title": "Melamchi River",
                "point": {"coordinates": [85.68, 27.95]},
                "waterLevel": 7.8,
                "dangerLevel": 6.5,
                "waterLevelOn": "2026-08-11T10:15:00+05:45",
                "modifiedOn": "2026-08-11T10:15:00+05:45",
                "status": "ABOVE DANGER LEVEL",
            }]
        }
        record = next(BipadRiverAdapter(fetch_json=lambda _: response).read())
        self.assertEqual(record.source_type, "hydrology")
        self.assertEqual(record.payload["river_level_m"], 7.8)
        self.assertEqual(record.payload["flood_threshold_m"], 6.5)
        self.assertEqual(record.payload["latitude"], 27.95)

    def test_road_incident_becomes_closure_signal(self):
        response = {
            "results": [{
                "id": 7,
                "title": "Highway blocked by landslide",
                "description": "Road closed near the bridge",
                "point": {"coordinates": [85.68, 27.95]},
                "reportedOn": "2026-08-11T11:10:00+05:45",
                "modifiedOn": "2026-08-11T11:10:00+05:45",
                "verified": True,
            }]
        }
        record = next(BipadIncidentAdapter("infrastructure", fetch_json=lambda _: response).read())
        self.assertEqual(record.payload["status"], "closed")
        self.assertEqual(record.payload["event_type"], "ROAD_CLOSURE")

    def test_river_record_with_null_level_remains_a_valid_normal_observation(self):
        response = {
            "results": [{
                "id": 43,
                "title": "Station without current level",
                "point": {"coordinates": [85.68, 27.95]},
                "waterLevel": None,
                "dangerLevel": 6.5,
                "modifiedOn": "2026-08-11T10:15:00+05:45",
            }]
        }
        record = next(BipadRiverAdapter(fetch_json=lambda _: response).read())
        self.assertEqual(record.payload["event_type"], "NORMAL")
        self.assertNotIn("river_level_m", record.payload)
