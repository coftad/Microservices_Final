import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv(
        "AUTH_DATABASE_URL",
        "postgresql://postgres:password@db:5432/main"
    )
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretchangeme")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour

settings = Settings()
