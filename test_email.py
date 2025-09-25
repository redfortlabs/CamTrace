# quick test script to confirm email works before wiring it into the report job

import sys, pathlib
from pathlib import Path

# Make sure we can import from ./src
sys.path.append(str(Path(__file__).parent / "src"))

# Load .env from project root (same folder as this script)
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

from camtrace.alert_email import send_email

if __name__ == "__main__":
    subject = "CamTrace test email"
    body = "If you see this, Gmail SMTP is working 🎉"
    send_email(subject, body)
    print("✅ Test email sent. Check your inbox.")
