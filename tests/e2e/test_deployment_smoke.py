"""Smoke contract for a deployed AEGIS ingestion service.

Run with ``AEGIS_DEPLOYMENT_URL=https://...``.  Pulls are opt-in because live
providers have rate limits and should not be called by a routine health check.
"""

from __future__ import annotations

import json
import os
import unittest
import urllib.request


class DeploymentSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base_url = os.getenv("AEGIS_DEPLOYMENT_URL", "").rstrip("/")
        if not cls.base_url:
            raise unittest.SkipTest("set AEGIS_DEPLOYMENT_URL to verify a deployed ingestion service")

    def get(self, path: str) -> dict:
        with urllib.request.urlopen(f"{self.base_url}{path}", timeout=20) as response:
            self.assertEqual(response.status, 200)
            return json.loads(response.read().decode())

    def test_deployment_contract(self) -> None:
        self.assertEqual(self.get("/health")["status"], "ok")
        self.assertEqual(self.get("/ready")["status"], "ready")
        self.assertIn("sources", self.get("/sources/health"))


if __name__ == "__main__":
    unittest.main()
