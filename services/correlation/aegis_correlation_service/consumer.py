from __future__ import annotations

import json
from typing import Any, Callable


class NormalizedEventConsumer:
    def __init__(self, bootstrap_servers: str, handler: Callable[[dict[str, Any]], None], group_id: str = "aegis-correlation") -> None:
        from kafka import KafkaConsumer

        self.consumer = KafkaConsumer(
            "normalized.events",
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            enable_auto_commit=False,
            value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        )
        self.handler = handler

    def consume_once(self, timeout_ms: int = 1000) -> int:
        processed = 0
        for records in self.consumer.poll(timeout_ms=timeout_ms).values():
            for record in records:
                self.handler(record.value)
                processed += 1
        if processed:
            self.consumer.commit()
        return processed

    def close(self) -> None:
        self.consumer.close()
