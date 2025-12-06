from fastapi import FastAPI
from .database import Base, engine
from .routers import stats
import asyncio
from .consumer import consume_events

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Create database tables
    Base.metadata.create_all(bind=engine)
    # Start consumer in background
    asyncio.create_task(consume_events())

app.include_router(stats.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}