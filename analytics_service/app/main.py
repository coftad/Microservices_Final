from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import stats
from .database import engine, Base
from .consumer import consume_events
import asyncio

app = FastAPI(title="Analytics Service")

# ADD CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Create database tables
    Base.metadata.create_all(bind=engine)
    # Start consumer in background
    asyncio.create_task(consume_events())

app.include_router(stats.router)

@app.get("/")
def read_root():
    return {"message": "Analytics Service"}