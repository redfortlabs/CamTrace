#!/usr/bin/env python3
"""
Placeholder agent that POSTs a fake event to the CamTrace /ingest endpoint.

In real usage, you might tail pfSense logs or summarize flows from a SPAN port,
then POST JSON records here.
"""
import requests, datetime

def main():
    evt = {
        "camera_id":"example_cam",
        "dst_ip":"8.8.8.8",
        "dst_port":53,
        "protocol":"udp",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }
    r = requests.post("http://localhost:8000/ingest", json=evt, timeout=5)
    print(r.status_code, r.text)

if __name__ == "__main__":
    main()
