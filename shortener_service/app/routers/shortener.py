from fastapi import APIRouter, Depends, HTTPException, Request, Header
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
import requests
import os

from app.database import SessionLocal
from app.models import ShortURL
from app.schemas import URLCreate, URLResponse
from app.utils import generate_short_code
from app.config import settings
from app.security import verify_token
from app.kafka_producer import send_url_hit

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/shorten", response_model=URLResponse)
def create_short_url(payload: URLCreate, user=Depends(verify_token), db: Session = Depends(get_db)):
    # user is now verified!
    print("Authenticated user:", user)

    short_code = generate_short_code()

    db_obj = ShortURL(
        short_code=short_code,
        original_url=payload.original_url,
        hit_count=0
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    short_url = f"{settings.BASE_URL}/{short_code}"

    return URLResponse(short_url=short_url, original_url=db_obj.original_url)


@router.get("/{short_code}")
async def redirect_url(short_code: str, request: Request, db: Session = Depends(get_db)):
    url_entry = db.query(ShortURL).filter(ShortURL.short_code == short_code).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="URL not found")

    # Update hit count
    url_entry.hit_count += 1
    db.commit()

    # Send event to Kafka asynchronously
    user_agent = request.headers.get("user-agent", "unknown")
    await send_url_hit(short_code, user_agent)

    return RedirectResponse(url=url_entry.original_url)


