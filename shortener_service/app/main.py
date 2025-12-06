from fastapi import FastAPI
from app.database import Base, engine
from app import models
from app.routers import shortener

# Create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shortener Service")

app.include_router(shortener.router)
