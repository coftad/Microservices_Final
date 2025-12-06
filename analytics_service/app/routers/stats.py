from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Hit

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/stats/{short_code}")
def get_stats(short_code: str, db: Session = Depends(get_db)):
    hits = db.query(Hit).filter(Hit.short_code == short_code).count()
    return {"short_code": short_code, "total_hits": hits}

@router.get("/stats")
def list_all(db: Session = Depends(get_db)):
    results = db.query(Hit.short_code, func.count(Hit.id)).group_by(Hit.short_code).all()
    return {"summary": [{"short_code": s, "hits": h} for s, h in results]}
