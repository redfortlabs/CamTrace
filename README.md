# CamTrace (Minimal MVP)

A tight-scope service to observe where home cameras talk on the internet.

**Scope**
- Python + FastAPI service
- One enrichment pass: RDNS + ASN + GeoIP (via MaxMind)
- YAML allowlist per camera
- Daily Markdown report + basic email alert on out-of-allowlist destinations
- Prometheus metrics + Grafana dashboard JSON (no custom UI)

> This is *not* a packet sniffer. It ingests summarized connection events (camera_id, dst_ip, dst_port, protocol, timestamp). Send logs from your firewall (pfSense/OPNsense) or a lightweight agent to `POST /ingest`.

## Quick Start

1) **Python env**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) **MaxMind DBs** (required for ASN/GeoIP)
- Create a free MaxMind account and download:
  - GeoLite2-ASN.mmdb
  - GeoLite2-City.mmdb
- Put them under `maxmind/` or set absolute paths via `.env`:

```
MAXMIND_ASN_DB=maxmind/GeoLite2-ASN.mmdb
MAXMIND_CITY_DB=maxmind/GeoLite2-City.mmdb
```

3) **Allowlist**
Edit `allowlist.yaml`. Example:
```yaml
cameras:
  porch_cam:
    allowed_asns: [15169, 20940]   # Google, Akamai (example)
    allowed_domains:
      - "nvr.local"
      - "update.vendor.example"
    allowed_cidrs:
      - "192.168.1.0/24"
      - "203.0.113.0/24"
  garage_cam:
    allowed_asns: [15169]
```

4) **Run**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

5) **Send a sample event**
```bash
curl -X POST http://localhost:8000/ingest   -H "Content-Type: application/json"   -d '{
    "camera_id":"porch_cam",
    "dst_ip":"8.8.8.8",
    "dst_port":53,
    "protocol":"udp",
    "timestamp":"2025-09-17T12:00:00Z"
  }'
```

6) **Metrics**
Visit `http://localhost:8000/metrics` for Prometheus.

7) **Report**
- Automatic daily report at 23:55 local time to `reports/`.
- Also emailed when there are *violations* (requires SMTP env vars). You can also trigger on demand:
```
curl -X POST http://localhost:8000/admin/report
```

## Environment (.env)

```
# MaxMind
MAXMIND_ASN_DB=maxmind/GeoLite2-ASN.mmdb
MAXMIND_CITY_DB=maxmind/GeoLite2-City.mmdb

# Email (optional but needed for alerts)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=username
SMTP_PASSWORD=app_password
SMTP_FROM=camtrace@example.com
ALERT_RECIPIENTS=you@example.com,security@example.com
```

## Data model (SQLite)

- `events` — raw ingested events + enrichment fields
- `violations` — subset of events that violate allowlist

## Ingestion format

```json
{
  "camera_id": "string",
  "dst_ip": "string (IPv4/IPv6)",
  "dst_port": 443,
  "protocol": "tcp|udp|icmp|other",
  "timestamp": "ISO8601 string"
}
```

## pfSense / OPNsense notes

- Configure firewall to **syslog** outbound connection logs to a small log forwarder that POSTs to `/ingest`.
- Or use a tiny agent on your LAN switch SPAN/mirror port to summarize flows and POST here (see `agent/placeholder_agent.py`).

## Grafana

- Import `grafana/dashboard.json`.
- Add a Prometheus data source pointing to this service's `/metrics` (via Prometheus server scraping or direct Agent).

## License

MIT (for this scaffold). You are responsible for your local laws and privacy compliance.
