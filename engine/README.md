# ScriptFlow AI

Assessment 3 script/voiceover-to-B-roll service.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -e ".[test]"
cp .env.example .env
uvicorn app.main:app --reload --port 8000 --env-file .env
```

Open http://localhost:8000/docs. Run tests with `pytest`; batch run with `python scripts/batch_runner.py tests/inputs.json --out test-pack`. Docker: `cp .env.example .env && docker compose up --build`.

## Real providers

- **Narration:** set `TTS_PROVIDER=edge-tts` in `.env`. Edge TTS needs outbound network access. If the provider fails, the job emits a warning and uses silent timing audio; inspect the manifest and do not call that a narrated video.
- **Stock footage:** request a Pexels API key and set `FOOTAGE_PROVIDER=pexels` and `PEXELS_API_KEY=...` in the backend-only `.env`. The adapter uses the Pexels video search endpoint, downloads MP4 clips, trims/crops them into scene segments, and preserves the video page URL, licence name, and contributor attribution in the timeline/manifest. If the key is missing or a provider/download fails, it falls back to a generated placeholder that is explicitly not commercially verified.
- Pexels' licence permits commercial use, but depicted people, trademarks, logos, and other third-party rights still need review. Add a prominent Pexels link/credit in any public frontend that displays or uses Pexels results, and follow the current API and licence terms.
- Never expose `PEXELS_API_KEY` in frontend variables or public logs.

## API

- `POST /api/v1/broll/jobs` — script/scene list.
- `POST /api/v1/broll/jobs/upload` — audio upload (MP3/WAV/M4A; transcription requires the optional `audio` extra).
- `GET /api/v1/jobs/{id}` — status/progress/result.
- `GET /api/v1/jobs/{id}/files/{filename}` — download artifacts.
- `POST /api/v1/jobs/{id}/retry` — retry a failed job.
- OpenAPI contract: `openapi.yaml`.

## Current limits

Job state is process-local, not durable. No public demo, database/queue, object storage, signed callbacks, remote audio URL ingestion, authenticated users, rate limiting, subtitle burn-in, or comprehensive codec/black-frame/audio-sync validation is configured. The live Pexels API path is unit-tested with a mocked response but has not been verified against a real key in this environment. Ten-input performance, human relevance and cost metrics are not yet measured.

See `REPORT.md`, `SOURCES.md`, `AI_USE.md`, and `../docs/ROADMAP.md`.
