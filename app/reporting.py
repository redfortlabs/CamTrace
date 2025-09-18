from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .config import ALERT_RECIPIENTS
from .emailer import send_email
from .models import Event


def generate_markdown_report(
    db_session: Session, *, since_hours: int = 24
) -> Tuple[str, List[Event]]:
    """
    Build a Markdown report for events within the last `since_hours`.
    Returns the markdown string and the list of violating events.
    """
    cutoff = datetime.utcnow() - timedelta(hours=since_hours)

    stmt_events = (
        select(Event)
        .where(Event.timestamp >= cutoff)
        .order_by(Event.timestamp.desc())
    )
    rows: List[Event] = list(db_session.execute(stmt_events).scalars())

    violations: List[Event] = [e for e in rows if e.violation == 1]

    lines: List[str] = [
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
        lines.append(
            "| time (UTC) | camera | dst_ip | dst_port | protocol | "
            "ASN | AS Org | RDNS | location |"
        )
        lines.append("|---|---|---:|---:|---|---:|---|---|---|")
        for e in violations[:500]:
            loc = ", ".join([x for x in [e.city, e.region, e.country] if x])
            lines.append(
                "| {ts} | {cam} | {ip} | {port} | {proto} | {asn} | {asorg} | "
                "{rdns} | {loc} |".format(
                    ts=e.timestamp.isoformat(),
                    cam=e.camera_id,
                    ip=e.dst_ip,
                    port=e.dst_port,
                    proto=e.protocol,
                    asn=e.asn or "",
                    asorg=e.as_org or "",
                    rdns=e.rdns or "",
                    loc=loc,
                )
            )

        for e in violations[:500]:
            loc = ", ".join([x for x in [e.city, e.region, e.country] if x])
            lines.append(
                "| {ts} | {cam} | {ip} | {port} | {proto} | {asn} | {asorg} | "
                "{rdns} | {loc} |".format(
                    ts=e.timestamp.isoformat(),
                    cam=e.camera_id,
                    ip=e.dst_ip,
                    port=e.dst_port,
                    proto=e.protocol,
                    asn=e.asn or "",
                    asorg=e.as_org or "",
                    rdns=e.rdns or "",
                    loc=loc,
                )
            )
    else:
        lines.append("_No violations in window._")

    lines += ["", "## Totals by Camera", ""]

    stmt_totals = (
        select(Event.camera_id, func.count())
        .where(Event.timestamp >= cutoff)
        .group_by(Event.camera_id)
    )
    totals = list(db_session.execute(stmt_totals).all())

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
    """
    Persist the Markdown report to reports/report_YYYYmmdd_HHMMSS.md.
    Returns the file path.
    """
    Path("reports").mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = Path(f"reports/report_{ts}.md")
    path.write_text(md, encoding="utf-8")
    return str(path)


def daily_report(db_session: Session) -> str:
    """
    Generate, write, and (if needed) email the daily report.
    Sends email only when violations are present and recipients are configured.
    Returns the report file path.
    """
    md, violations = generate_markdown_report(db_session)
    path = write_report(md)

    if violations and ALERT_RECIPIENTS:
        # Best-effort email; ignore send failure to avoid breaking the job.
        send_email("CamTrace: violations detected", md, ALERT_RECIPIENTS)

    return path
