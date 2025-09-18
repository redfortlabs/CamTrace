from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from pathlib import Path
from typing import List
from .models import Event
from .emailer import send_email
from .config import ALERT_RECIPIENTS

def generate_markdown_report(db_session: Session, *, since_hours: int = 24) -> tuple[str, List[Event]]:
    cutoff = datetime.utcnow() - timedelta(hours=since_hours)
    stmt = select(Event).where(Event.timestamp >= cutoff).order_by(Event.timestamp.desc())
    rows = list(db_session.execute(stmt).scalars())

    violations = [e for e in rows if e.violation == 1]

    lines = [
        f"# CamTrace Daily Report ({datetime.utcnow().isoformat()}Z)",
        "",
        f"Window: last {since_hours} hours",
        f"Total events: {len(rows)}",
        f"Violations: {len(violations)}",
        "",
        "## Violations",
        "",
    ]
    if violations:
        lines.append("| time (UTC) | camera | dst_ip | dst_port | protocol | ASN | AS Org | RDNS | location |")
        lines.append("|---|---|---:|---:|---|---:|---|---|---|")
        for e in violations[:500]:
            loc = ", ".join([x for x in [e.city, e.region, e.country] if x])
            lines.append(f"| {e.timestamp.isoformat()} | {e.camera_id} | {e.dst_ip} | {e.dst_port} | {e.protocol} | {e.asn or ''} | {e.as_org or ''} | {e.rdns or ''} | {loc} |")
    else:
        lines.append("_No violations in window._")

    lines += ["", "## Totals by Camera", ""]

    # totals
    stmt_tot = select(Event.camera_id, func.count()).where(Event.timestamp >= cutoff).group_by(Event.camera_id)
    totals = list(db_session.execute(stmt_tot).all())
    if totals:
        lines.append("| camera | events |")
        lines.append("|---|---:|")
        for cam, cnt in totals:
            lines.append(f"| {cam} | {cnt} |")
    else:
        lines.append("_No events._")

    md = "\n".join(lines)
    return md, violations

def write_report(md: str) -> str:
    Path("reports").mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = Path(f"reports/report_{ts}.md")
    path.write_text(md, encoding="utf-8")
    return str(path)

def daily_report(db_session: Session):
    md, violations = generate_markdown_report(db_session)
    path = write_report(md)
    # Alert only if there are violations
    if violations and ALERT_RECIPIENTS:
        send_email("CamTrace: violations detected", md, ALERT_RECIPIENTS)
    return path
