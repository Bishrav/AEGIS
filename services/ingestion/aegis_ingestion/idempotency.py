from __future__ import annotations

from .normalize import deduplication_key


class RedisIdempotencyStore:
    def __init__(self, redis_url: str, ttl_seconds: int = 604800) -> None:
        import redis

        self.client = redis.Redis.from_url(redis_url, decode_responses=True)
        self.ttl_seconds = ttl_seconds

    def claim(self, record) -> bool:
        key = f"aegis:idempotency:{deduplication_key(record)}"
        return bool(self.client.set(key, "1", nx=True, ex=self.ttl_seconds))

