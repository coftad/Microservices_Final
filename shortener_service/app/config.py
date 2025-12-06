import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/main")
    KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
    KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "url_hits")
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

settings = Settings()