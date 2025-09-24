#!/usr/bin/env bash
# Auto-activate .venv if camtrace not on PATH
if ! command -v camtrace >/dev/null 2>&1; then
  if [[ -f ".venv/bin/activate" ]]; then
    echo "[*] Activating local .venv"
    source .venv/bin/activate
  fi
fi
# pcap_to_camtrace.sh — capture → flows.jsonl → enriched.csv (results/<timestamp>/)
# Requirements: tcpdump, tshark (from Wireshark), jq, camtrace (installed in your venv)

set -euo pipefail

# --- defaults (override via env or flags) ---
IFACE="${IFACE:-en0}"       # macOS default interface; on Linux often 'eth0'
COUNT="${COUNT:-200}"       # number of packets if duration not set
DURATION="${DURATION:-}"    # seconds to capture; if set, overrides COUNT
RESULTS_DIR="results/$(date +%Y%m%d-%H%M%S)"
PCAP_FILE="$RESULTS_DIR/capture.pcap"
JSONL_FILE="$RESULTS_DIR/flows.jsonl"
CSV_FILE="$RESULTS_DIR/enriched.csv"

# --- usage/help ---
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<EOF
Usage: ./pcap_to_camtrace.sh [--pcap path/to/file.pcap] [--iface en0] [--count 200] [--duration 10]

Flags:
  --pcap FILE       Use an existing pcap instead of capturing
  --iface IFACE     Network interface to capture on (default: $IFACE)
  --count N         Capture N packets (default: $COUNT)
  --duration SEC    Capture for SEC seconds (overrides --count)

Env overrides:
  IFACE=en0 COUNT=200 DURATION=10

Examples:
  ./pcap_to_camtrace.sh --iface en0 --count 400
  ./pcap_to_camtrace.sh --duration 10
  ./pcap_to_camtrace.sh --pcap my.pcap
EOF
  exit 0
fi

# --- tiny flag parser ---
PCAP_ARG=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --pcap) PCAP_ARG="$2"; shift 2 ;;
    --iface) IFACE="$2"; shift 2 ;;
    --count) COUNT="$2"; shift 2 ;;
    --duration) DURATION="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

# --- deps check ---
need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing '$1'. Install it first."; exit 1; }; }
need tcpdump
need tshark
need jq
need camtrace

# --- ensure results dir ---
mkdir -p "$RESULTS_DIR"

# --- capture (unless using an existing pcap) ---
if [[ -n "$PCAP_ARG" ]]; then
  echo "[*] Using existing PCAP: $PCAP_ARG"
  PCAP_FILE="$PCAP_ARG"
else
  echo "[*] Capturing packets on interface: $IFACE"
  echo "    Output: $PCAP_FILE"

  # Filter to common Internet traffic; avoids local broadcast/mDNS noise.
  BPF_FILTER='tcp or udp and (port 53 or port 80 or port 443)'

  if [[ -n "$DURATION" ]]; then
    # Capture for N seconds using tcpdump's built-in timer (no 'timeout' needed on macOS)
    sudo tcpdump -i "$IFACE" -w "$PCAP_FILE" -G "$DURATION" -W 1 $BPF_FILTER
  else
    # Capture N packets
    sudo tcpdump -i "$IFACE" -w "$PCAP_FILE" -c "$COUNT" $BPF_FILTER
  fi
fi

# --- convert PCAP → JSONL (flow-like lines) ---
echo "[*] Converting PCAP → JSONL: $JSONL_FILE"
tshark -r "$PCAP_FILE" -T json \
| jq -c '.[] 
  | select(._source.layers.ip) 
  | {
      ts: (._source.layers.frame["frame.time_epoch"]),
      proto: (._source.layers.ip["ip.proto"]),
      src_ip: (._source.layers.ip["ip.src"]),
      dst_ip: (._source.layers.ip["ip.dst"]),
      src_port: (
        (._source.layers.tcp["tcp.srcport"] // ._source.layers.udp["udp.srcport"]) // empty
      ),
      dst_port: (
        (._source.layers.tcp["tcp.dstport"] // ._source.layers.udp["udp.dstport"]) // empty
      )
    }' > "$JSONL_FILE"

LINES=$(wc -l < "$JSONL_FILE" | tr -d ' ')
echo "[*] Wrote $LINES JSON lines → $JSONL_FILE"

# --- enrich with CamTrace ---
echo "[*] Enriching with CamTrace → $CSV_FILE"
camtrace --enrich --in "$JSONL_FILE" --out "$CSV_FILE" --csv

# --- final status message ---
echo
echo "[+] Done!"
echo "    PCAP:   $PCAP_FILE"
echo "    JSONL:  $JSONL_FILE"
echo "    CSV:    $CSV_FILE"
echo
echo "Tip: to preview in terminal:"
echo "    head -n 5 $CSV_FILE"
echo
echo "On macOS you can open the CSV directly in Numbers/Excel:"
echo "    open $CSV_FILE"
echo

