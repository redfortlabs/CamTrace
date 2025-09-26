# tests/test_report.py
from contextlib import suppress
from pathlib import Path

from camtrace.report_job import run_daily_report_and_alert

with suppress(ImportError, OSError):
    from dotenv import load_dotenv  # dev-only

    load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")


def test_run_daily_report_smoke(monkeypatch):
    """Basic smoke test for report job."""
    assert callable(run_daily_report_and_alert)
