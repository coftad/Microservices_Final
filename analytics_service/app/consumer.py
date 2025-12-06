
import asyncio
from aiokafka import AIOKafkaConsumer
import json
from .database import SessionLocal
from .models import Hit
from app.config import settings
from datetime import datetime

async def consume_events():
    print(f"Starting consumer with settings:")
    print(f"Bootstrap servers: {settings.KAFKA_BOOTSTRAP}")
    print(f"Topic: {settings.KAFKA_TOPIC}")
    print(f"Group ID: {settings.KAFKA_GROUP_ID}")

    while True:  # Keep trying to connect
        try:
            consumer = AIOKafkaConsumer(
                settings.KAFKA_TOPIC,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP,
                group_id=settings.KAFKA_GROUP_ID,
                auto_offset_reset='earliest',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )

            await consumer.start()
            print("✓ Successfully connected to Kafka consumer")

            try:
                async for msg in consumer:
                    try:
                        data = msg.value
                        print(f"Received message: {data}")

                        db = SessionLocal()
                        try:
                            hit = Hit(
                                short_code=data["short_code"],
                                user_agent=data.get("user_agent", "unknown"),
                                timestamp=datetime.utcnow()
                            )
                            db.add(hit)
                            db.commit()
                            print(f"✓ Successfully stored hit for {data['short_code']}")
                        except Exception as db_error:
                            print(f"Database error: {db_error}")
                            db.rollback()
                        finally:
                            db.close()
                    except json.JSONDecodeError as e:
                        print(f"Failed to decode message: {e}")
                    except Exception as e:
                        print(f"Error processing message: {e}")

            except Exception as e:
                print(f"Consumer loop error: {e}")
            finally:
                await consumer.stop()

        except Exception as e:
            print(f"Failed to connect to Kafka: {e}")
            await asyncio.sleep(5)  # Wait before retrying