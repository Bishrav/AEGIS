import unittest

from aegis_ingestion.live_adapters import OpenMeteoWeatherAdapter


class LiveAdapterTests(unittest.TestCase):
    def test_open_meteo_response_maps_to_raw_records(self):
        response = {
            "hourly": {
                "time": ["2026-08-11T00:00", "2026-08-11T01:00"],
                "precipitation": [12.5, 18.0],
                "temperature_2m": [22.1, 21.7],
            }
        }
        adapter = OpenMeteoWeatherAdapter(27.95, 85.68, fetch_json=lambda _: response)
        records = list(adapter.read())
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].source_id, "open-meteo-weather")
        self.assertEqual(records[0].payload["rainfall_mm"], 12.5)
        self.assertEqual(records[1].record_id, "open-meteo-weather:2026-08-11T01:00")

