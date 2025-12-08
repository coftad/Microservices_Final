from aiokafka import AIOKafkaProducer
import json
import os
import asyncio

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "url_hits")

_producer = None

async def get_producer():
    """Get or create the Kafka producer"""
    global _producer
    if _producer is None:
        try:
            _producer = AIOKafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await _producer.start()
            print("✓ Kafka producer started for shortener service")
        except Exception as e:
            print(f"Failed to start Kafka producer: {e}")
    return _producer

async def send_url_hit(short_code: str, user_agent: str = None):
    """Send URL hit event to Kafka"""
    producer = await get_producer()
    if producer:
        try:
            message = {
                "short_code": short_code,
                "user_agent": user_agent,
                "timestamp": str(__import__('datetime').datetime.utcnow().isoformat())
            }
            await producer.send(KAFKA_TOPIC, value=message)
            print(f"✓ Sent URL hit for {short_code}")
        except Exception as e:
            print(f"Failed to send URL hit: {e}")

async def send_endpoint_metric(metric_data: dict):
    """Send endpoint metric to Kafka"""
    producer = await get_producer()
    if producer:
        try:
            await producer.send("endpoint_metrics", value=metric_data)
            print(f"✓ Sent metric for {metric_data['method']} {metric_data['endpoint']}")
        except Exception as e:
            print(f"Failed to send metric: {e}")

async def close_producer():
    """Close the Kafka producer"""
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None