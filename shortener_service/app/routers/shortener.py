from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import ShortURL
from app.schemas import URLCreate, URLResponse
from app.utils import generate_short_code
from app.config import settings
from app.security import verify_token
from app.kafka_producer import send_hit_event

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
async def redirect(short_code: str, request: Request, db: Session = Depends(get_db)):
    record = db.query(ShortURL).filter(ShortURL.short_code == short_code).first()
    if not record:
        raise HTTPException(status_code=404, detail="URL not found")

    # Increment hit_count (optional)
    record.hit_count += 1
    db.commit()

    # Send event to Kafka
    ua = request.headers.get("User-Agent")
    await send_hit_event(short_code, ua)

    return {"redirect_to": record.original_url}


