from aiokafka import AIOKafkaProducer
import json
from app.config import settings

producer = None

async def get_producer():
    global producer
    if producer is None:
        producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await producer.start()
    return producer

async def send_hit_event(short_code: str, user_agent: str | None):
    prod = await get_producer()
    event = {
        "short_code": short_code,
        "user_agent": user_agent
    }
    await prod.send_and_wait(settings.KAFKA_TOPIC, event)
