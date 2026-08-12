import json
import os
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@unittest.skipUnless(os.getenv("AEGIS_INTEGRATION") == "1", "set AEGIS_INTEGRATION=1 to run Docker integration tests")
class RuntimeIntegrationTests(unittest.TestCase):
    base_url = os.getenv("AEGIS_INGESTION_URL", "http://localhost:8002")

    def request(self, path: str, method: str = "GET") -> dict:
        request = Request(f"{self.base_url}{path}", method=method)
        last_error = None
        for attempt in range(15):
            try:
                with urlopen(request, timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    return json.load(response)
            except (ConnectionResetError, TimeoutError, URLError, HTTPError) as error:
                last_error = error
                if isinstance(error, HTTPError) and error.code < 500:
                    raise
                if attempt == 14:
                    raise
                time.sleep(2)
        raise AssertionError(f"request failed after retries: {last_error}")

    def test_running_stack_exposes_ingestion_contract(self):
        self.assertEqual(self.request("/health")["status"], "ok")
        self.assertEqual(self.request("/ready")["status"], "ready")
        replay = self.request("/replay/weather", method="POST")
        self.assertEqual(replay["source_type"], "weather")
        self.assertIn("published", replay)
        self.assertIn("sources", self.request("/sources/health"))
