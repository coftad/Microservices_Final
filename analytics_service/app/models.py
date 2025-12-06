from sqlalchemy import Column, Integer, String, DateTime
from .database import Base

class Hit(Base):
    __tablename__ = "hits"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String(255), nullable=False)
    user_agent = Column(String(255))
    timestamp = Column(DateTime, nullable=False)