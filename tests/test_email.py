# tests/test_email.py
from contextlib import suppress
from pathlib import Path

from camtrace.alert_email import send_email

with suppress(ImportError, OSError):
    from dotenv import load_dotenv  # dev-only

    load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")


def test_send_email_smoke(monkeypatch):
    # Prevent real sends if needed:
    # monkeypatch.setattr("camtrace.alert_email.send_email", lambda *args, **kwargs: None)
    assert callable(send_email)
