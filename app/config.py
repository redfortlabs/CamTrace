import os
from dotenv import load_dotenv

load_dotenv()

MAXMIND_ASN_DB = os.getenv("MAXMIND_ASN_DB", "maxmind/GeoLite2-ASN.mmdb")
MAXMIND_CITY_DB = os.getenv("MAXMIND_CITY_DB", "maxmind/GeoLite2-City.mmdb")

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM", "camtrace@example.com")
ALERT_RECIPIENTS = [e.strip() for e in os.getenv("ALERT_RECIPIENTS", "").split(",") if e.strip()]
