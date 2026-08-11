from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Callable, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    initial_delay_seconds: float = 0.1
    max_delay_seconds: float = 2.0

    def run(self, operation: Callable[[], T]) -> T:
        last_error: Exception | None = None
        for attempt in range(self.max_attempts):
            try:
                return operation()
            except Exception as exc:
                last_error = exc
                if attempt == self.max_attempts - 1:
                    break
                time.sleep(min(self.initial_delay_seconds * (2**attempt), self.max_delay_seconds))
        assert last_error is not None
        raise last_error


@dataclass
class SourceHealth:
    source_id: str
    status: str = "unknown"
    success_count: int = 0
    failure_count: int = 0
    last_error: str | None = None
    last_success_at: str | None = None
    last_failure_at: str | None = None


class SourceHealthRegistry:
    def __init__(self) -> None:
        self.sources: dict[str, SourceHealth] = {}

    def success(self, source_id: str) -> None:
        health = self.sources.setdefault(source_id, SourceHealth(source_id))
        health.status = "healthy"
        health.success_count += 1
        health.last_success_at = datetime.now(UTC).isoformat()

    def failure(self, source_id: str, error: Exception) -> None:
        health = self.sources.setdefault(source_id, SourceHealth(source_id))
        health.status = "degraded"
        health.failure_count += 1
        health.last_error = str(error)
        health.last_failure_at = datetime.now(UTC).isoformat()

    def snapshot(self) -> list[dict[str, object]]:
        return [health.__dict__.copy() for health in self.sources.values()]


class RetryingPublisher:
    def __init__(self, publisher, policy: RetryPolicy) -> None:
        self.publisher = publisher
        self.policy = policy

    def publish(self, event) -> None:
        self.policy.run(lambda: self.publisher.publish(event))

    def dead_letter(self, record, reason: str) -> None:
        self.policy.run(lambda: self.publisher.dead_letter(record, reason))

    def close(self) -> None:
        self.publisher.close()
