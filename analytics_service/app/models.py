from sqlalchemy import Column, Integer, String, DateTime, Float
from .database import Base

class Hit(Base):
    __tablename__ = "hits"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String(255), nullable=False)
    user_agent = Column(String(255))
    timestamp = Column(DateTime, nullable=False)

class EndpointMetric(Base):
    """Track usage statistics for all API endpoints"""
    __tablename__ = "endpoint_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(100), nullable=False)
    endpoint = Column(String(500), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    latency_ms = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    user_id = Column(Integer, nullable=True)