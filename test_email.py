# quick test script to confirm email works before wiring it into the report job

import sys, pathlib

# Add ./src to sys.path so "camtrace" can be imported without installing package
sys.path.append(str(pathlib.Path(__file__).parent.joinpath("src")))

from camtrace.alert_email import send_email

if __name__ == "__main__":
    subject = "CamTrace test email"
    body = "If you see this, Gmail SMTP is working 🎉"
    send_email(subject, body)
    print("✅ Test email sent. Check your inbox.")
