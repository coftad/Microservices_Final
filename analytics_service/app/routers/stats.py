from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from ..database import SessionLocal
from ..models import Hit, EndpointMetric
from ..security import verify_admin_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/stats/{short_code}")
def get_stats(short_code: str, db: Session = Depends(get_db), user: dict = Depends(verify_admin_token)):
    hits = db.query(Hit).filter(Hit.short_code == short_code).count()
    return {"short_code": short_code, "total_hits": hits}

@router.get("/stats")
def list_all(db: Session = Depends(get_db), user: dict = Depends(verify_admin_token)):
    results = db.query(Hit.short_code, func.count(Hit.id)).group_by(Hit.short_code).all()
    return {"summary": [{"short_code": s, "hits": h} for s, h in results]}

@router.get("/endpoint-stats")
def get_endpoint_statistics(
    service: str = Query(None, description="Filter by service name"),
    hours: int = Query(24, description="Last N hours"),
    db: Session = Depends(get_db),
    user: dict = Depends(verify_admin_token)
):
    """Get comprehensive endpoint usage statistics"""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    query = db.query(EndpointMetric).filter(EndpointMetric.timestamp >= cutoff)
    
    if service:
        query = query.filter(EndpointMetric.service_name == service)
    
    # Aggregate by endpoint
    stats = db.query(
        EndpointMetric.service_name,
        EndpointMetric.endpoint,
        EndpointMetric.method,
        func.count(EndpointMetric.id).label('total_requests'),
        func.avg(EndpointMetric.latency_ms).label('avg_latency_ms'),
        func.max(EndpointMetric.latency_ms).label('max_latency_ms'),
        func.min(EndpointMetric.latency_ms).label('min_latency_ms')
    ).filter(
        EndpointMetric.timestamp >= cutoff
    ).group_by(
        EndpointMetric.service_name,
        EndpointMetric.endpoint,
        EndpointMetric.method
    ).all()
    
    return {
        "period_hours": hours,
        "endpoints": [
            {
                "service": s.service_name,
                "endpoint": s.endpoint,
                "method": s.method,
                "total_requests": s.total_requests,
                "avg_latency_ms": round(s.avg_latency_ms, 2),
                "max_latency_ms": round(s.max_latency_ms, 2),
                "min_latency_ms": round(s.min_latency_ms, 2)
            }
            for s in stats
        ]
    }