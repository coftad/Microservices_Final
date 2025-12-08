import asyncio
from aiokafka import AIOKafkaConsumer
import json
from .database import SessionLocal
from .models import Hit, EndpointMetric
from app.config import settings
from datetime import datetime

async def consume_url_hits():
    """Consumer for URL hit events"""
    print(f"Starting URL hits consumer with settings:")
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
            print("✓ Successfully connected to Kafka consumer for URL hits")

            try:
                async for msg in consumer:
                    try:
                        data = msg.value
                        print(f"Received URL hit message: {data}")

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

async def consume_endpoint_metrics():
    """Consumer for endpoint metrics events"""
    ENDPOINT_METRICS_TOPIC = "endpoint_metrics"
    
    print(f"Starting endpoint metrics consumer")
    print(f"Bootstrap servers: {settings.KAFKA_BOOTSTRAP}")
    print(f"Topic: {ENDPOINT_METRICS_TOPIC}")
    print(f"Group ID: {settings.KAFKA_GROUP_ID}")

    while True:  # Keep trying to connect
        try:
            consumer = AIOKafkaConsumer(
                ENDPOINT_METRICS_TOPIC,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP,
                group_id=settings.KAFKA_GROUP_ID,
                auto_offset_reset='earliest',
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )

            await consumer.start()
            print("✓ Successfully connected to Kafka consumer for endpoint metrics")

            try:
                async for msg in consumer:
                    try:
                        data = msg.value
                        print(f"Received endpoint metric message: {data}")

                        db = SessionLocal()
                        try:
                            metric = EndpointMetric(
                                service_name=data["service_name"],
                                endpoint=data["endpoint"],
                                method=data["method"],
                                status_code=data["status_code"],
                                latency_ms=data["latency_ms"],
                                timestamp=datetime.fromisoformat(data["timestamp"]),
                                user_id=data.get("user_id")
                            )
                            db.add(metric)
                            db.commit()
                            print(f"✓ Successfully stored metric for {data['service_name']}{data['endpoint']}")
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

async def consume_events():
    """Start both consumers concurrently"""
    await asyncio.gather(
        consume_url_hits(),
        consume_endpoint_metrics()
    )