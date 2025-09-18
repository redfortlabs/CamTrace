from fastapi import FastAPI, Response
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
import os
from .models import Base, get_engine
from .routers import ingest, admin
from .enrich import init_geoip, close_geoip
from .metrics import metrics_response
from .reporting import daily_report

app = FastAPI(title="CamTrace")

# routers
app.include_router(ingest.router)
app.include_router(admin.router)

# metrics endpoint
@app.get("/metrics")
def metrics():
    body, status, headers = metrics_response()
    return Response(content=body, status_code=status, headers=headers)

# startup/shutdown
@app.on_event("startup")
def on_startup():
    # DB
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    # GeoIP
    init_geoip()

     # NEW: allow disabling scheduler for tests/CI
    if os.getenv("DISABLE_SCHEDULER", "0") == "1":
        return

    
    from sqlalchemy.orm import sessionmaker
    from .models import get_sessionmaker
    SessionLocal = get_sessionmaker(engine)
    
    def job():
        db = SessionLocal()
        try:
            daily_report(db)
        finally:
            db.close()

    tz = os.getenv("TZ", "America/Chicago")
    sched = BackgroundScheduler(timezone=timezone(tz))
    sched.add_job(job, "cron", hour=23, minute=55, id="daily_report")
    sched.start()
    app.state.scheduler = sched

@app.on_event("shutdown")
def on_shutdown():
    close_geoip()
    if getattr(app.state, "scheduler", None):
        app.state.scheduler.shutdown()

