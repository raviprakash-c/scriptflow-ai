# ScriptFlow AI

Assessment 3 script/voiceover-to-B-roll service. Honest current status: the local preview creates placeholder visuals, and default TTS is silent timing audio. The project does not yet pass all IncuBrix must-haves. Please review each limitation before presenting any claim.

## Run

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -e ".[test]"
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs; test using `pytest`; batch run using `python scripts/batch_runner.py tests/inputs.json --out test-pack`. Docker: `cp .env.example .env && docker compose up --build`.

## Current limits

The service has a versioned API, background jobs, progress/status, download links, a scene planner, mock footage adapter, FFmpeg placeholder render path, SRT/timeline/manifest outputs, tests, OpenAPI spec, and batch runner. Job state is process-local. Commercial stock provider, TTS by default, remote audio URL ingestion, durable storage/queue, signed callbacks, subtitle burn-in and public deployment are not configured. Local placeholders are explicitly not commercially verified; do not mark the corresponding Must-have as passed.

See REPORT.md, SOURCES.md, and AI_USE.md.
