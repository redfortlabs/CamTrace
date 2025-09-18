from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_metrics_endpoint_works():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert b"camtrace_events_total" in r.content


def test_admin_initdb():
    r = client.post("/admin/initdb")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
