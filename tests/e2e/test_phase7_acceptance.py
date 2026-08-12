"""Phase 7 local acceptance test for the running AEGIS Compose stack."""

from __future__ import annotations

import http.cookiejar
import json
import os
import time
import unittest
import urllib.request

API_URL = os.getenv("AEGIS_API_URL", "http://localhost:8000")
CORRELATION_URL = os.getenv("AEGIS_CORRELATION_URL", "http://localhost:8003")
EVIDENCE_URL = os.getenv("AEGIS_EVIDENCE_URL", "http://localhost:8004")


class Phase7Acceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if os.getenv("AEGIS_E2E") != "1":
            raise unittest.SkipTest("set AEGIS_E2E=1 to run against the local Compose stack")
        cls.cookies = http.cookiejar.CookieJar()
        cls.client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cls.cookies))

    @classmethod
    def request(cls, url: str, method: str = "GET", payload: dict | None = None) -> tuple[int, dict]:
        body = json.dumps(payload).encode() if payload is not None else None
        request = urllib.request.Request(url, data=body, method=method)
        if body is not None:
            request.add_header("Content-Type", "application/json")
        with cls.client.open(request, timeout=10) as response:
            return response.status, json.loads(response.read().decode())

    def test_authenticated_vertical_slice(self) -> None:
        status, login = self.request(f"{API_URL}/api/v1/auth/login", "POST", {"username": "analyst", "password": "analyst-dev"})
        self.assertEqual(status, 200)
        self.assertEqual(login["role"], "ANALYST")
        status, me = self.request(f"{API_URL}/api/v1/me")
        self.assertEqual(status, 200)
        self.assertEqual(me["role"], "ANALYST")

        document_id = f"phase7-{int(time.time())}"
        status, document = self.request(f"{EVIDENCE_URL}/documents", "POST", {
            "document_id": document_id,
            "title": "Phase 7 flood response bulletin",
            "text": "Heavy rainfall caused flooding and road disruption in Sindhupalchok.",
            "source_uri": "https://example.test/phase7-bulletin",
        })
        self.assertEqual(status, 200)
        self.assertTrue(document["evidence_ids"])

        incident_id = f"phase7-{int(time.time())}"
        events = [
            {"event_id": f"{incident_id}-rain", "event_type": "HEAVY_RAIN", "occurred_at": "2026-08-12T09:00:00Z", "entities": [{"type": "DISTRICT", "value": "Sindhupalchok"}]},
            {"event_id": f"{incident_id}-flood", "event_type": "FLOOD", "occurred_at": "2026-08-12T10:00:00Z", "entities": [{"type": "DISTRICT", "value": "Sindhupalchok"}]},
            {"event_id": f"{incident_id}-road", "event_type": "ROAD_CLOSURE", "occurred_at": "2026-08-12T11:00:00Z", "entities": [{"type": "DISTRICT", "value": "Sindhupalchok"}]},
        ]
        status, incident = self.request(f"{CORRELATION_URL}/correlate", "POST", {"incident_id": incident_id, "events": events})
        self.assertEqual(status, 200)
        self.assertEqual(incident["incident_id"], incident_id)
        status, detail = self.request(f"{API_URL}/api/v1/incidents/{incident_id}")
        self.assertEqual(status, 200)
        self.assertIn("risk", detail)
        status, updated = self.request(f"{API_URL}/api/v1/incidents/{incident_id}/status", "PATCH", {"status": "ACKNOWLEDGED"})
        self.assertEqual(status, 200)
        self.assertEqual(updated["status"], "ACKNOWLEDGED")
        status, noted = self.request(f"{API_URL}/api/v1/incidents/{incident_id}/notes", "POST", {"note": "Phase 7 acceptance note", "author": "analyst"})
        self.assertEqual(status, 200)
        self.assertTrue(noted["notes"])
        status, evidence = self.request(f"{API_URL}/api/v1/incidents/{incident_id}/evidence?query=flood&top_k=5")
        self.assertEqual(status, 200)
        self.assertTrue(evidence["hits"])
        stream = self.client.open(urllib.request.Request(f"{API_URL}/api/v1/events/stream"), timeout=5)
        try:
            self.assertEqual(stream.readline().decode().strip(), "event: heartbeat")
        finally:
            stream.close()


if __name__ == "__main__":
    unittest.main()
