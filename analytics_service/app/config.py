
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database Configuration
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@db:5432/main"
    )

    # Kafka Configuration
    KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
    KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "url_hits")
    KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "analytics-consumer-group")
    KAFKA_AUTO_OFFSET_RESET = os.getenv("KAFKA_AUTO_OFFSET_RESET", "earliest")
    KAFKA_SESSION_TIMEOUT_MS = int(os.getenv("KAFKA_SESSION_TIMEOUT_MS", "30000"))
    KAFKA_HEARTBEAT_INTERVAL_MS = int(os.getenv("KAFKA_HEARTBEAT_INTERVAL_MS", "3000"))

    # Service Configuration
    SERVICE_NAME = "analytics_service"
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", "8002"))

settings = Settings()