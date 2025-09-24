# CamTrace — IP Enrichment (PTR / ASN / Geo)

CamTrace is a lightweight tool that takes raw network flow logs from IoT and other connected devices and makes them easier to understand. Out of the box, flow records usually only show IP addresses — which can be cryptic and hard to interpret.  

CamTrace enriches those flows by adding:

- Reverse DNS (PTR) lookups → shows the hostname tied to an IP  
- ASN ownership → identifies the network owner (e.g., Google, Cloudflare)  
- GeoIP data → adds country, city, and latitude/longitude  

This makes it much simpler to answer questions like:
- “Which external services is this device talking to?”  
- “Are flows leaving the country?”  
- “Which organizations own the IP ranges my IoT devices connect to?”

Everything runs locally on your machine using MaxMind’s free GeoLite2 databases, so no data is sent outside your environment.

---

## Features

- Reverse DNS (PTR) lookups  
- ASN + Organization lookups (GeoLite2-ASN)  
- Country / City / Lat/Lon enrichment (GeoLite2-City)  
- JSONL → CSV conversion for easy analysis in Excel/Numbers  
- **Live capture helper (`camtrace-capture`)**: runs `tcpdump → tshark → enrich` end-to-end  

---

## Setup

1. **Clone the repository and create a virtual environment:**
   ```bash
   git clone https://github.com/redfortlabs/CamTrace.git
   cd CamTrace
   python3 -m venv .venv
   source .venv/bin/activate

2. Install CamTrace in editable mode:

pip install -e .

3. Place the MaxMind databases in the project at:

data/maxmind/GeoLite2-ASN.mmdb
data/maxmind/GeoLite2-City.mmdb

4. Create a .env file in the project root with:

MAXMIND_ASN_DB=./data/maxmind/GeoLite2-ASN.mmdb
MAXMIND_CITY_DB=./data/maxmind/GeoLite2-City.mmdb
DNS_RESOLVER=1.1.1.1
ENRICH_IPS=true

---

## Quick Start (Static JSONL)

Process the included sample flow file:

camtrace --enrich --in examples/flows.jsonl --out flows.csv --csv

This will produce flows.csv with PTR, ASN, and GeoIP enrichment.

---

## Quick Start (Live Capture)

You can also capture a short burst of packets, convert them to flows, and enrich them in one step:

camtrace-capture --duration 10
# Results in: results/<timestamp>/enriched.csv

Other usage examples:

camtrace-capture --count 500              # capture 500 packets (default iface)
camtrace-capture --iface en0 --duration 15
camtrace-capture --pcap path/to/file.pcap # process an existing PCAP

When it completes, the command prints exactly where the files are:

[+] Done!
    PCAP:   results/2025.../capture.pcap
    JSONL:  results/2025.../flows.jsonl
    CSV:    results/2025.../enriched.csv

Example Output

From examples/flows.jsonl:

{"ts":"2025-09-23T14:30:00Z","proto":"udp","src_ip":"192.168.1.10","dst_ip":"8.8.8.8","dst_port":53,"dst_ptr":"dns.google","dst_asn":15169,"dst_as_org":"GOOGLE","dst_country_iso":"US","dst_country_name":"United States"}
{"ts":"2025-09-23T14:30:05Z","proto":"udp","src_ip":"192.168.1.10","dst_ip":"1.1.1.1","dst_port":53,"dst_ptr":"one.one.one.one","dst_asn":13335,"dst_as_org":"CLOUDFLARENET"}

## Notes

Private/reserved IPs are skipped (columns appear but empty).

PTR lookups use the configured DNS_RESOLVER in .env.

Numeric fields (ports, bytes, pkts, ASN, lat/lon) are written as numbers in CSV.

Live capture requires tcpdump, tshark, and jq.

On macOS: brew install tcpdump wireshark jq

## Tests

Run the test suite:

pytest -q

Expected:
.                                                                    [100%]
1 passed in 0.xx s

## Updating MaxMind DBs

When you download fresh MaxMind GeoLite2 DBs, replace the .mmdb files in:

data/maxmind/

and rerun CamTrace. No code changes required.
