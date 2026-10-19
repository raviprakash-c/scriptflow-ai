from fastapi.testclient import TestClient
from app.main import app
from app.store import reset_store

client = TestClient(app)


def setup_function():
    reset_store()


def test_health():
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/ready").json()["status"] == "ready"


def test_missing_input_rejected():
    assert client.post("/api/v1/broll/jobs", json={}).status_code == 422


def test_script_job_accepted():
    response = client.post(
        "/api/v1/broll/jobs",
        headers={"Idempotency-Key": "a"},
        json={"script": "Save money. Track spending.", "aspect_ratios": ["16:9"]},
    )
    assert response.status_code == 202
    assert response.json()["status"] in ("queued", "running", "succeeded")


def test_idempotency_replay():
    payload = {"script": "Save money. Track spending.", "aspect_ratios": ["16:9"]}
    first = client.post("/api/v1/broll/jobs", headers={"Idempotency-Key": "stable"}, json=payload)
    second = client.post("/api/v1/broll/jobs", headers={"Idempotency-Key": "stable"}, json=payload)
    assert first.json()["job_id"] == second.json()["job_id"]
    assert second.json()["idempotent_replay"] is True


def test_idempotency_conflict():
    client.post(
        "/api/v1/broll/jobs",
        headers={"Idempotency-Key": "conflict"},
        json={"script": "first", "aspect_ratios": ["16:9"]},
    )
    response = client.post(
        "/api/v1/broll/jobs",
        headers={"Idempotency-Key": "conflict"},
        json={"script": "different", "aspect_ratios": ["16:9"]},
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "IDEMPOTENCY_KEY_REUSED"


def test_missing_job_structured_error():
    response = client.get("/api/v1/jobs/nope")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "JOB_NOT_FOUND"
