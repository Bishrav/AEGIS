"""Failure-injection acceptance tests for ingestion reliability behavior."""

from __future__ import annotations

import unittest

from aegis_ingestion.reliability import RetryingPublisher, RetryPolicy, SourceHealthRegistry


class FailureRecoveryTests(unittest.TestCase):
    def test_transient_publisher_failure_recovers_with_retry(self) -> None:
        class FlakyPublisher:
            def __init__(self) -> None:
                self.attempts = 0

            def publish(self, _event) -> None:
                self.attempts += 1
                if self.attempts < 3:
                    raise ConnectionError("broker unavailable")

            def dead_letter(self, _record, _reason) -> None:
                raise AssertionError("transient failure should not dead-letter")

            def close(self) -> None:
                pass

        publisher = FlakyPublisher()
        RetryingPublisher(publisher, RetryPolicy(max_attempts=3, initial_delay_seconds=0)).publish({"id": "event-1"})
        self.assertEqual(publisher.attempts, 3)

    def test_permanent_source_failure_is_visible_as_degraded(self) -> None:
        health = SourceHealthRegistry()
        health.failure("bipad", TimeoutError("upstream timeout"))
        snapshot = health.snapshot()
        self.assertEqual(snapshot[0]["status"], "degraded")
        self.assertEqual(snapshot[0]["failure_count"], 1)
        self.assertEqual(snapshot[0]["last_error"], "upstream timeout")


if __name__ == "__main__":
    unittest.main()
