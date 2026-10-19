"""SQLite-backed job and idempotency store.

SQLite makes job state survive API process restarts on a single host. It is not a
replacement for a distributed queue or shared database in multi-replica deployments.
"""
import json
import sqlite3
import threading
import uuid
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from .config import settings

_lock = threading.RLock()
_db_path = Path(settings.job_db_path).resolve()


def now():
    return datetime.now(timezone.utc).isoformat()


def _connect():
    _db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(_db_path, timeout=15, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA busy_timeout=15000")
    connection.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            record_json TEXT NOT NULL
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS idempotency_keys (
            key TEXT PRIMARY KEY,
            digest TEXT NOT NULL,
            job_id TEXT NOT NULL REFERENCES jobs(job_id)
        )
    """)
    return connection


def _decode(row):
    return json.loads(row["record_json"]) if row else None


def create_job(payload, key, digest, input_path=None):
    with _lock, closing(_connect()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            if key:
                existing = connection.execute(
                    "SELECT digest, job_id FROM idempotency_keys WHERE key = ?", (key,)
                ).fetchone()
                if existing:
                    row = connection.execute(
                        "SELECT record_json FROM jobs WHERE job_id = ?", (existing["job_id"],)
                    ).fetchone()
                    connection.execute("COMMIT")
                    if existing["digest"] == digest:
                        return _decode(row), "replay"
                    return None, "conflict"
            stamp = now()
            job_id = str(uuid.uuid4())
            record = {
                "job_id": job_id, "status": "queued", "progress": 0, "stage": "queued",
                "created_at": stamp, "updated_at": stamp, "request": payload,
                "input_path": str(input_path) if input_path else None, "result": None, "error": None,
            }
            connection.execute(
                "INSERT INTO jobs(job_id, record_json) VALUES (?, ?)",
                (job_id, json.dumps(record, ensure_ascii=False)),
            )
            if key:
                connection.execute(
                    "INSERT INTO idempotency_keys(key, digest, job_id) VALUES (?, ?, ?)",
                    (key, digest, job_id),
                )
            connection.execute("COMMIT")
            return record, "created"
        except Exception:
            connection.execute("ROLLBACK")
            raise


def get_job(job_id):
    with _lock, closing(_connect()) as connection:
        row = connection.execute("SELECT record_json FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
        return _decode(row)


def patch_job(job_id, **changes):
    with _lock, closing(_connect()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            row = connection.execute("SELECT record_json FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
            record = _decode(row)
            if record is None:
                raise KeyError(f"Unknown job id: {job_id}")
            record.update(changes)
            record["updated_at"] = now()
            connection.execute(
                "UPDATE jobs SET record_json = ? WHERE job_id = ?",
                (json.dumps(record, ensure_ascii=False), job_id),
            )
            connection.execute("COMMIT")
            return record
        except Exception:
            connection.execute("ROLLBACK")
            raise


def list_jobs():
    with _lock, closing(_connect()) as connection:
        rows = connection.execute("SELECT record_json FROM jobs").fetchall()
        records = [_decode(row) for row in rows]
        return sorted(records, key=lambda item: item["created_at"], reverse=True)


def recover_interrupted_jobs():
    """Mark queued/running jobs interrupted by a process restart as failed, not stuck."""
    recovered = 0
    with _lock, closing(_connect()) as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            rows = connection.execute("SELECT job_id, record_json FROM jobs").fetchall()
            for row in rows:
                record = _decode(row)
                if record["status"] in {"queued", "running"}:
                    record.update({
                        "status": "failed", "progress": 0, "stage": "interrupted", "updated_at": now(),
                        "error": {
                            "code": "SERVER_RESTARTED",
                            "message": "The server restarted before this job completed. Retry the job.",
                            "retryable": True, "details": {},
                        },
                    })
                    connection.execute(
                        "UPDATE jobs SET record_json = ? WHERE job_id = ?",
                        (json.dumps(record, ensure_ascii=False), row["job_id"]),
                    )
                    recovered += 1
            connection.execute("COMMIT")
        except Exception:
            connection.execute("ROLLBACK")
            raise
    return recovered


def reset_store():
    """Clear persisted jobs for tests and local development only."""
    with _lock, closing(_connect()) as connection:
        connection.execute("DELETE FROM idempotency_keys")
        connection.execute("DELETE FROM jobs")
