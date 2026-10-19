from fastapi.testclient import TestClient
from app.main import app
from app.store import _jobs,_keys
client=TestClient(app)
def setup_function():
    _jobs.clear();_keys.clear()
def test_health():
    assert client.get("/health").json()["status"]=="ok"
    assert client.get("/ready").json()["status"]=="ready"
def test_missing_input_rejected():
    assert client.post("/api/v1/broll/jobs",json={}).status_code==422
def test_script_job_accepted():
    r=client.post("/api/v1/broll/jobs",headers={"Idempotency-Key":"a"},json={"script":"Save money. Track spending.","aspect_ratios":["16:9"]})
    assert r.status_code==202 and r.json()["status"] in ("queued","running","succeeded")
def test_idempotency_replay():
    p={"script":"Save money. Track spending.","aspect_ratios":["16:9"]}
    a=client.post("/api/v1/broll/jobs",headers={"Idempotency-Key":"stable"},json=p)
    b=client.post("/api/v1/broll/jobs",headers={"Idempotency-Key":"stable"},json=p)
    assert a.json()["job_id"]==b.json()["job_id"] and b.json()["idempotent_replay"] is True
def test_idempotency_conflict():
    client.post("/api/v1/broll/jobs",headers={"Idempotency-Key":"conflict"},json={"script":"first","aspect_ratios":["16:9"]})
    r=client.post("/api/v1/broll/jobs",headers={"Idempotency-Key":"conflict"},json={"script":"different","aspect_ratios":["16:9"]})
    assert r.status_code==409 and r.json()["error"]["code"]=="IDEMPOTENCY_KEY_REUSED"
def test_missing_job_structured_error():
    r=client.get("/api/v1/jobs/nope")
    assert r.status_code==404 and r.json()["error"]["code"]=="JOB_NOT_FOUND"
