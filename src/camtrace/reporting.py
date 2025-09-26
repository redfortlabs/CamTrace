# src/camtrace/reporting.py
"""Prefer reports under project root ./reports/ (not inside src/).
If a report exists, return the latest and parse violation counts from its
'Violations' table. If no report exists yet, create a fresh stub for today
with 0 violations.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

REPORTS_DIR = Path("reports")  # project-root reports/, not inside src/


def _find_latest_report() -> Path | None:
    if not REPORTS_DIR.exists():
        return None
    candidates = sorted(REPORTS_DIR.glob("*_camtrace_daily_report.md"))
    return candidates[-1] if candidates else None


def _parse_violations(md_text: str) -> tuple[int, dict[str, int]]:
    total = 0
    by_device: dict[str, int] = {}

    lines = [ln.strip() for ln in md_text.splitlines()]
    in_table = False
    headers: list[str] = []
    device_idx = None

    for i, ln in enumerate(lines):
        if not in_table and ln.startswith("|") and "Device" in ln and "|" in ln:
            headers = [h.strip() for h in ln.strip("|").split("|")]
            try:
                device_idx = headers.index("Device")
            except ValueError:
                device_idx = None
            if i + 1 < len(lines) and set(lines[i + 1].strip()) <= {"|", "-", " "}:
                in_table = True
            continue

        if in_table:
            if not (ln.startswith("|") and ln.endswith("|")):
                break
            if set(ln.strip()) <= {"|", "-", ":", " "}:
                continue

            cells = [c.strip() for c in ln.strip("|").split("|")]
            total += 1
            if device_idx is not None and device_idx < len(cells):
                dev = cells[device_idx]
                by_device[dev] = by_device.get(dev, 0) + 1

    return total, by_device


def _write_stub_report() -> Path:
    REPORTS_DIR.mkdir(exist_ok=True)
    path = (
        REPORTS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}_camtrace_daily_report.md"
    )
    body = f"""# CamTrace Daily Report — {datetime.now().strftime('%B %d, %Y')}

**Coverage window:** 00:00–23:59 (America/Chicago)  
**Ingested events:** 0  
**Unique devices:** 0  
**Violations:** 0  
**New destinations first seen today:** 0

---

## Violations
| Time (CT) | Device | dst_ip:port | RDNS | ASN | Geo | Severity | Reason |
|---|---|---|---|---|---|---|---|
"""
    path.write_text(body, encoding="utf-8")
    return path


def generate_markdown_report() -> tuple[Path, int, dict[str, int]]:
    REPORTS_DIR.mkdir(exist_ok=True)
    latest = _find_latest_report()
    if latest and latest.exists():
        md = latest.read_text(encoding="utf-8")
        total, by_dev = _parse_violations(md)
        return latest, total, by_dev
    created = _write_stub_report()
    return created, 0, {}
