# examples/enrich_demo.py
import os
import sys
from dotenv import load_dotenv

# Ensure src is on sys.path for a quick demo run
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from camtrace.ip_enricher import resolve_ip  # noqa: E402

load_dotenv()

ips = ["8.8.8.8", "1.1.1.1"]

for ip in ips:
    rec = resolve_ip(ip)
    print("---", ip, "---")
    print(rec.model_dump())
