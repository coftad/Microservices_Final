from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base

class ShortURL(Base):
    __tablename__ = "short_urls"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String(20), unique=True, index=True)
    original_url = Column(String(2048))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    hit_count = Column(Integer, default=0)  # optional convenience
