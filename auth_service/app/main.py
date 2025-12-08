from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth
from .database import engine, Base
import time
from datetime import datetime
import json
from aiokafka import AIOKafkaProducer
import os

# Create tables

app = FastAPI(title="Auth Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple Kafka producer for auth service
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
producer = None

@app.on_event("startup")
async def startup_event():
    global producer
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not create tables on startup: {e}")

    try:
        producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        await producer.start()
    except Exception as e:
        print(f"Failed to start Kafka producer: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    global producer
    if producer:
        await producer.stop()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    latency_ms = (time.time() - start_time) * 1000
    
    user_id = None
    
    metric_data = {
        "service_name": "auth_service",
        "endpoint": str(request.url.path),
        "method": request.method,
        "status_code": response.status_code,
        "latency_ms": latency_ms,
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id
    }
    
    if producer:
        try:
            await producer.send("endpoint_metrics", value=metric_data)
        except Exception as e:
            print(f"Failed to send metrics: {e}")
    
    return response

app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Auth Service"}
