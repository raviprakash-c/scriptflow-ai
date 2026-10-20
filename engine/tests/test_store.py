import app.store as store


def test_job_state_and_idempotency_persist_between_connections(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "_db_path", tmp_path / "jobs.sqlite3")
    payload = {"script": "Persist this job"}
    job, state = store.create_job(payload, "persist-key", "digest-1")
    assert state == "created"

    store.patch_job(job["job_id"], status="failed", stage="test", progress=0)
    loaded = store.get_job(job["job_id"])
    assert loaded["status"] == "failed"
    assert loaded["stage"] == "test"

    replay, state = store.create_job(payload, "persist-key", "digest-1")
    assert state == "replay"
    assert replay["job_id"] == job["job_id"]


def test_idempotency_key_rejects_different_payload(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "_db_path", tmp_path / "jobs.sqlite3")
    store.create_job({"script": "first"}, "same-key", "digest-1")
    job, state = store.create_job({"script": "second"}, "same-key", "digest-2")
    assert job is None
    assert state == "conflict"


def test_interrupted_jobs_are_marked_retryable(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "_db_path", tmp_path / "jobs.sqlite3")
    job, _ = store.create_job({"script": "queued"}, None, "digest")
    assert store.recover_interrupted_jobs() == 1
    recovered = store.get_job(job["job_id"])
    assert recovered["status"] == "failed"
    assert recovered["error"]["code"] == "SERVER_RESTARTED"
    assert recovered["error"]["retryable"] is True
