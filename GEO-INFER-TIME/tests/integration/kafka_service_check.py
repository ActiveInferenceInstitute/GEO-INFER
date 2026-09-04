"""Explicit live-broker check, outside the hermetic pytest collection.

Run against a disposable Kafka broker with --bootstrap-servers HOST:PORT.
The check creates and deletes its own unique topic and tests redelivery after
an unacknowledged read, then resumption after a committed record.
"""

import argparse
import asyncio
import json
from contextlib import aclosing
from datetime import timedelta
from uuid import uuid4

from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic

from geo_infer_time import KafkaIngestAdapter, StreamProcessor


async def check_broker(bootstrap_servers: str) -> None:
    topic = "geo-infer-time-check-" + uuid4().hex
    admin = AIOKafkaAdminClient(
        bootstrap_servers=bootstrap_servers, request_timeout_ms=10000
    )
    await asyncio.wait_for(admin.start(), 15)
    created = False
    try:
        await admin.create_topics(
            [NewTopic(topic, num_partitions=1, replication_factor=1)]
        )
        created = True
        producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
        try:
            await asyncio.wait_for(producer.start(), 15)
            for index in range(2):
                await producer.send_and_wait(
                    topic,
                    json.dumps({"timestamp": index, "value": index + 10}).encode(),
                )
        finally:
            await producer.stop()
        config = {
            "bootstrap_servers": bootstrap_servers,
            "topic": topic,
            "group_id": topic,
            "max_retries": 0,
            "receive_timeout": 20,
            "consumer_options": {"auto_offset_reset": "earliest"},
        }
        first = KafkaIngestAdapter(config)
        async with aclosing(first.stream_data()) as records:
            unacknowledged = await anext(records)
            assert first.parse_record(unacknowledged)[1] == 10
        replay = StreamProcessor(timedelta(seconds=10))
        assert (
            await replay.ingest_adapter_stream(
                KafkaIngestAdapter(config), max_messages=1
            )
            == 1
        )
        assert replay.buffer[0]["value"] == 10
        resumed = StreamProcessor(timedelta(seconds=10))
        assert (
            await resumed.ingest_adapter_stream(
                KafkaIngestAdapter(config), max_messages=1
            )
            == 1
        )
        assert resumed.buffer[0]["value"] == 11
        assert (
            replay.buffer[0]["metadata"]["_kafka"]["offset"] + 1
            == resumed.buffer[0]["metadata"]["_kafka"]["offset"]
        )
        print(
            "PASS: actual Kafka produce, unacknowledged replay, "
            "commit, and group resumption"
        )
    finally:
        try:
            if created:
                await admin.delete_topics([topic])
        finally:
            await admin.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap-servers", required=True)
    arguments = parser.parse_args()
    asyncio.run(check_broker(arguments.bootstrap_servers))
