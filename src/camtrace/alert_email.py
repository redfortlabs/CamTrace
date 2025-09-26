# creating a drop-in helper for sending alerts via Gmail.

import os
import smtplib
from email.mime.text import MIMEText


def _get_env(name: str, required: bool = True, default: str | None = None) -> str:
    """Fetch an environment variable or raise if missing."""
    val = os.getenv(name, default)
    if required and not val:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val


def send_email(subject: str, body_text: str) -> None:
    """
    Send a plaintext email using Gmail SMTP + App Password.
    Env vars must be set in .env or system environment:
      SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_APP_PASSWORD,
      SMTP_FROM, SMTP_TO
    """
    host = _get_env("SMTP_HOST")
    port = int(_get_env("SMTP_PORT"))
    user = _get_env("SMTP_USER")
    app_pw = _get_env("SMTP_APP_PASSWORD")
    from_addr = _get_env("SMTP_FROM")
    to_addr = _get_env("SMTP_TO")

    msg = MIMEText(body_text, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr

    with smtplib.SMTP(host, port, timeout=20) as server:
        server.starttls()  # upgrade connection to TLS
        server.login(user, app_pw)
        server.sendmail(from_addr, [to_addr], msg.as_string())
