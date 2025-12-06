from fastapi import FastAPI
from app.database import Base, engine
from app import models
from app.routers import auth

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")

app.include_router(auth.router)
