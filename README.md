#CamTrace — IP Enrichment (PTR / ASN / Geo)
CamTrace enriches network flow logs with: 
- Reverse DNS (PTR) lookups 
- ASN ownership (via MaxMind GeoLite2-ASN)
- GeoIP country/city/lat/long (via MaxMind GeoLite2-City)
- This runs fully locally using your downloaded MaxMind databases.

##Setup
1. Place the MaxMind databases in the project at:
data/maxmind/GeoLite2-ASN.mmdb data/maxmind/GeoLite2-City.mmdb
2. Create a `.env` file in the project root with:

MAXMIND_ASN_DB=./data/maxmind/GeoLite2-ASN.mmdb
MAXMIND_CITY_DB=./data/maxmind/GeoLite2-City.mmdb
DNS_RESOLVER=1.1.1.1
ENRICH_IPS=true

- `DNS_RESOLVER` can be any resolver you trust (e.g. `8.8.8.8`).
- `ENRICH_IPS=false` will skip enrichment.

3. Set up a virtual environment and install:
/opt/homebrew/bin/python3 -m venv .venv
source .venv/bin/activate
pip install -e .

##Usage
Enrich flows and write CSV:
camtrace --enrich --in examples/flows.jsonl --out flows.csv --csv
Enrich flows and stream JSONL to stdout:
camtrace --enrich --in examples/flows.jsonl --out -

##Notes
- Private/reserved IPs are skipped (columns appear but empty).
- PTR lookups use the configured `DNS_RESOLVER` in `.env`.
- Numeric fields (ports, bytes, pkts, ASN, lat/lon) are written as real numbers in CSV.

##Tests
Run the test suite:
pytest -q

Expecteed: [100%] 1 passed in 0.xx s

##Updating MaxMind DBs
When you download fresh MaxMind GeoLite2 DBs, replace the `.mmdb` files in: data/maxmind/  
and rerun CamTrace. No code changes required.
