# ScriptFlow AI

Assessment 3 script/voiceover-to-B-roll service.

## Run locally on Windows PowerShell

From the engine directory:

    py -m venv .venv
    .venv\Scripts\Activate.ps1
    py -m pip install -e ".[test]"
    Copy-Item .env.example .env
    python -m uvicorn app.main:app --reload --port 8000 --env-file .env

## Run locally on macOS/Linux

From the engine directory:

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install -e ".[test]"
    cp .env.example .env
    python -m uvicorn app.main:app --reload --port 8000 --env-file .env

Open http://localhost:8000/docs. Run tests with python -m pytest. Batch run with python scripts/batch_runner.py tests/inputs.json --out test-pack. For Docker, copy .env.example to .env and run docker compose up --build.

If a managed Windows device blocks Python or pip through Application Control, use an approved Python environment or ask the administrator; do not try to bypass the policy.

## Real providers

- Narration: set TTS_PROVIDER=edge-tts in .env. Edge TTS needs outbound network access. If the provider fails, the job emits a warning and uses silent timing audio; inspect the manifest and do not call that a narrated video.
- Stock footage: set FOOTAGE_PROVIDER=pexels and add one or both backend-only keys: PEXELS_API_KEY and PIXABAY_API_KEY. The engine tries configured providers in order (Pexels then Pixabay), downloads MP4 clips, trims/crops them into scene segments, and preserves the source page URL, licence name, and contributor attribution in the timeline/manifest. If keys are missing or providers/downloads fail, it falls back to a generated placeholder that is explicitly not commercially verified.
- Pexels and Pixabay licences permit many commercial uses subject to their terms, but depicted people, trademarks, logos, and other third-party rights still need review. Show clear source attribution/links in any public frontend that displays or uses results. Do not redistribute stock clips as standalone media or use the APIs to build a competing stock library.
- Never expose PEXELS_API_KEY or PIXABAY_API_KEY in frontend variables or public logs.

## API

- POST /api/v1/broll/jobs — script/scene list.
- POST /api/v1/broll/jobs/upload — audio upload (MP3/WAV/M4A; transcription requires the optional audio extra).
- GET /api/v1/jobs — recent persisted job records.
- GET /api/v1/jobs/{id} — status/progress/result.
- GET /api/v1/jobs/{id}/files/{filename} — download artifacts.
- POST /api/v1/jobs/{id}/retry — retry a failed job.
- OpenAPI contract: openapi.yaml.

## Job persistence and deployment boundaries

SQLite persists job records and idempotency keys across API process restarts on a single host. On startup, queued/running records from a prior process are marked failed with a retryable SERVER_RESTARTED error instead of remaining stuck forever. Output files and the SQLite database must live on persistent storage; Docker Compose mounts ./outputs.

This is not a distributed queue: do not run multiple API replicas against local ephemeral files. Production deployment still needs a shared durable database/queue, authentication and authorization, rate limiting, storage lifecycle/cleanup, secure artifact access, and operational alerting.

## Current limits

Remote audio URL ingestion is not implemented; uploaded audio transcription requires the optional audio extra. Subtitle burn-in is enabled when requested and MP4 metadata is checked with ffprobe for H.264, expected dimensions, audio stream, duration and minimum file size. Black/frozen-frame detection and full audio-sync checks remain unimplemented. Provider adapters have mocked-response unit tests but have not been exercised with real API keys in this environment. Ten-input performance, human relevance and cost metrics are not yet measured.

See REPORT.md, SOURCES.md, AI_USE.md, and ../docs/ROADMAP.md.
