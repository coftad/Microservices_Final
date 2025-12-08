from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .routers import shortener
from .database import engine, Base
import time
from datetime import datetime
import asyncio
from .kafka_producer import get_producer, send_endpoint_metric, close_producer

app = FastAPI(title="URL Shortener Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Create database tables and initialize Kafka on startup"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not create tables on startup: {e}")
    
    # Initialize Kafka producer
    await get_producer()

@app.on_event("shutdown")
async def shutdown_event():
    """Close Kafka producer on shutdown"""
    await close_producer()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    latency_ms = (time.time() - start_time) * 1000
    
    # Extract user_id from token if present
    user_id = None
    auth_header = request.headers.get("authorization")
    if auth_header:
        # You could decode the JWT here to get user_id
        # For now, we'll leave it as None
        pass
    
    # Send metrics to Kafka
    metric_data = {
        "service_name": "shortener_service",
        "endpoint": str(request.url.path),
        "method": request.method,
        "status_code": response.status_code,
        "latency_ms": latency_ms,
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id
    }
    
    # Send asynchronously
    asyncio.create_task(send_endpoint_metric(metric_data))
    
    return response

app.include_router(shortener.router, tags=["shortener"])

@app.get("/")
def read_root():
    return {"message": "URL Shortener Service"}