from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models import get_engine, get_sessionmaker, Base
from ..reporting import daily_report
from ..enrich import init_geoip, close_geoip

engine = get_engine()
SessionLocal = get_sessionmaker(engine)

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/initdb")
def init_db():
    Base.metadata.create_all(bind=engine)
    return {"status": "ok"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/report")
def run_report(db: Session = Depends(get_db)):
    path = daily_report(db)
    return {"status": "ok", "report_path": path}

@router.post("/reload-geoip")
def reload_geoip():
    close_geoip()
    init_geoip()
    return {"status": "ok"}
