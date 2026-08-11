from __future__ import annotations

import json
from dataclasses import dataclass

from .models import CanonicalEvent, RawRecord
from .normalize import deduplication_key
from .serialization import canonical_event_to_dict, raw_record_to_dict


@dataclass(frozen=True)
class MinioSettings:
    endpoint_url: str
    access_key: str
    secret_key: str
    bucket: str = "aegis-raw"


class MinioRawPayloadStore:
    def __init__(self, settings: MinioSettings) -> None:
        import boto3

        self.settings = settings
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.endpoint_url,
            aws_access_key_id=settings.access_key,
            aws_secret_access_key=settings.secret_key,
            region_name="us-east-1",
        )
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.settings.bucket)
        except self.client.exceptions.ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in {"404", "NoSuchBucket"}:
                self.client.create_bucket(Bucket=self.settings.bucket)
            else:
                raise

    def put_if_absent(self, record: RawRecord) -> bool:
        key = self._object_key(record)
        try:
            self.client.head_object(Bucket=self.settings.bucket, Key=key)
            return False
        except self.client.exceptions.ClientError as exc:
            if exc.response.get("Error", {}).get("Code") not in {"404", "NoSuchKey"}:
                raise
        self.client.put_object(
            Bucket=self.settings.bucket,
            Key=key,
            Body=json.dumps(raw_record_to_dict(record)).encode("utf-8"),
            ContentType="application/json",
        )
        return True

    def _object_key(self, record: RawRecord) -> str:
        return f"raw/{record.source_id}/{record.record_id}.json"

    def object_uri(self, record: RawRecord) -> str:
        return f"s3://{self.settings.bucket}/{self._object_key(record)}"


class KafkaEventPublisher:
    def __init__(self, bootstrap_servers: str) -> None:
        from kafka import KafkaProducer

        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            key_serializer=lambda key: key.encode("utf-8"),
            value_serializer=lambda value: json.dumps(value).encode("utf-8"),
            acks="all",
            retries=5,
        )

    def publish(self, event: CanonicalEvent) -> None:
        self.producer.send(
            "normalized.events",
            key=str(event.event_id),
            value=canonical_event_to_dict(event),
        ).get(timeout=10)

    def dead_letter(self, record: RawRecord, reason: str) -> None:
        self.producer.send(
            "deadletter.ingestion",
            key=deduplication_key(record),
            value={"reason": reason, "record": raw_record_to_dict(record)},
        ).get(timeout=10)

    def close(self) -> None:
        self.producer.flush()
        self.producer.close()
