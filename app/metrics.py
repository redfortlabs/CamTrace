from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

events_total = Counter("camtrace_events_total", "Total ingested events", ["camera_id"])
violations_total = Counter("camtrace_violations_total", "Total violations", ["camera_id"])
dest_asn_total = Counter("camtrace_dest_asn_total", "Events by destination ASN", ["asn"])
last_event_timestamp = Gauge("camtrace_last_event_timestamp", "Unix ts of last event", ["camera_id"])

def metrics_response():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}
