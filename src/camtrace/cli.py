# src/camtrace/cli.py
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from typing import Dict, Any, Iterable

from dotenv import load_dotenv
from camtrace.enrich_adapter import enrich_flow_record


# ----------------- CLI args -----------------
def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="CamTrace: enrich flow JSONL with PTR/ASN/Geo (local MaxMind DBs)."
    )
    p.add_argument(
        "--enrich",
        action="store_true",
        default=os.getenv("ENRICH_IPS", "false").lower() == "true",
        help="Enrich IPs (default based on ENRICH_IPS env var).",
    )
    p.add_argument("--in", dest="infile", default="-", help="Input JSONL (default: stdin)")
    p.add_argument("--out", dest="outfile", default="-", help="Output (JSONL/CSV) (default: stdout)")
    p.add_argument(
        "--csv",
        action="store_true",
        help="Output CSV instead of JSONL",
    )
    return p.parse_args(argv)


# ----------------- I/O helpers -----------------
def iter_jsonl(fh) -> Iterable[Dict[str, Any]]:
    for line in fh:
        line = line.strip()
        if not line:
            continue
        yield json.loads(line)


def write_jsonl(records: Iterable[Dict[str, Any]], fh) -> None:
    for rec in records:
        fh.write(json.dumps(rec, separators=(",", ":")) + "\n")


CSV_COLUMNS = [
    "ts", "proto", "src_ip", "src_port", "dst_ip", "dst_port", "bytes", "pkts",
    "src_ptr", "src_asn", "src_as_org", "src_country_iso", "src_country_name",
    "src_region", "src_city", "src_latitude", "src_longitude",
    "dst_ptr", "dst_asn", "dst_as_org", "dst_country_iso", "dst_country_name",
    "dst_region", "dst_city", "dst_latitude", "dst_longitude",
]

def _as_int(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return ""

def _as_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return ""

NUMERIC_FIELDS = {
    "src_port": _as_int,
    "dst_port": _as_int,
    "bytes": _as_int,
    "pkts": _as_int,
    "src_asn": _as_int,
    "dst_asn": _as_int,
    "src_latitude": _as_float,
    "src_longitude": _as_float,
    "dst_latitude": _as_float,
    "dst_longitude": _as_float,
}

def write_csv(records: Iterable[Dict[str, Any]], fh) -> None:
    writer = csv.DictWriter(fh, fieldnames=CSV_COLUMNS, extrasaction="ignore")
    writer.writeheader()
    for rec in records:
        row = dict(rec)
        # coerce numerics
        for k, caster in NUMERIC_FIELDS.items():
            if k in row:
                row[k] = caster(row.get(k))
        writer.writerow(row)


# ----------------- Main -----------------
def main(argv=None) -> int:
    load_dotenv()
    args = parse_args(argv)

    in_fh = sys.stdin if args.infile in ("-", "") else open(args.infile, "r", encoding="utf-8")
    out_fh = sys.stdout if args.outfile in ("-", "") else open(args.outfile, "w", encoding="utf-8")

    try:
        records = iter_jsonl(in_fh)

     
        # optional enrichment (avoid self-referential generator)
        if args.enrich:
            orig_records = records  # capture the original iterator

            def gen(records_iter):
                for rec in records_iter:
                    if "src_ip" in rec or "dst_ip" in rec:
                        enrich_flow_record(rec)
                    yield rec

            records = gen(orig_records)


        # output
        if args.csv:
            write_csv(records, out_fh)
        else:
            write_jsonl(records, out_fh)
        return 0

    finally:
        if in_fh is not sys.stdin:
            in_fh.close()
        if out_fh is not sys.stdout:
            out_fh.close()


if __name__ == "__main__":
    raise SystemExit(main())
