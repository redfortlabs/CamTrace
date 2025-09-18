from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..schemas import IngestEvent
from ..models import Event, get_engine, get_sessionmaker
from ..enrich import geo_enrich
from ..allowlist import Allowlist
from ..metrics import events_total, violations_total, dest_asn_total, last_event_timestamp

engine = get_engine()
SessionLocal = get_sessionmaker(engine)
allowlist = Allowlist("allowlist.yaml")

router = APIRouter(prefix="/ingest", tags=["ingest"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("", status_code=201)
def ingest_event(evt: IngestEvent, db: Session = Depends(get_db)):
    try:
        ts = datetime.fromisoformat(evt.timestamp.replace("Z","+00:00"))
    except Exception:
        raise HTTPException(400, "Invalid timestamp; must be ISO8601")

    enrich = geo_enrich(evt.dst_ip)
    asn = enrich.get("asn")
    rdns = enrich.get("rdns")

    # Allowlist check
    is_allowed = allowlist.check(evt.camera_id, asn=asn, rdns=rdns, ip=evt.dst_ip)

    e = Event(
        camera_id=evt.camera_id,
        dst_ip=evt.dst_ip,
        dst_port=evt.dst_port,
        protocol=evt.protocol,
        timestamp=ts,
        rdns=enrich.get("rdns"),
        asn=enrich.get("asn"),
        as_org=enrich.get("as_org"),
        country=enrich.get("country"),
        region=enrich.get("region"),
        city=enrich.get("city"),
        latitude=enrich.get("latitude"),
        longitude=enrich.get("longitude"),
        violation=0 if is_allowed else 1,
    )
    db.add(e)
    db.commit()

    # metrics
    events_total.labels(evt.camera_id).inc()
    if asn:
        dest_asn_total.labels(str(asn)).inc()
    last_event_timestamp.labels(evt.camera_id).set(ts.timestamp())
    if not is_allowed:
        violations_total.labels(evt.camera_id).inc()

    return {"status": "ok", "violation": 0 if is_allowed else 1}
