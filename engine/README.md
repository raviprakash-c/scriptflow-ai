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
- **Stock footage:** set `FOOTAGE_PROVIDER=pexels`, and add one or both backend-only keys: `PEXELS_API_KEY=...`, `PIXABAY_API_KEY=...`. The engine tries configured providers in order (Pexels then Pixabay), downloads MP4 clips, trims/crops them into scene segments, and preserves the source page URL, licence name, and contributor attribution in the timeline/manifest. If keys are missing or providers/downloads fail, it falls back to a generated placeholder that is explicitly not commercially verified.
- Pexels and Pixabay licences permit many commercial uses subject to their terms, but depicted people, trademarks, logos, and other third-party rights still need review. Show clear source attribution/links in any public frontend that displays or uses results. Do not redistribute stock clips as standalone media or use the APIs to build a competing stock library.
- Never expose `PEXELS_API_KEY` or `PIXABAY_API_KEY` in frontend variables or public logs.

## API

- `POST /api/v1/broll/jobs` — script/scene list.
- `POST /api/v1/broll/jobs/upload` — audio upload (MP3/WAV/M4A; transcription requires the optional `audio` extra).
- `GET /api/v1/jobs/{id}` — status/progress/result.
- `GET /api/v1/jobs/{id}/files/{filename}` — download artifacts.
- `POST /api/v1/jobs/{id}/retry` — retry a failed job.
- OpenAPI contract: `openapi.yaml`.

## Current limits

Job state is process-local, not durable. No public demo, database/queue, object storage, signed callbacks, remote audio URL ingestion, authenticated users, rate limiting, subtitle burn-in, or comprehensive codec/black-frame/audio-sync validation is configured. Provider adapters have mocked-response unit tests but have not been exercised with real API keys in this environment. Ten-input performance, human relevance and cost metrics are not yet measured.

See `REPORT.md`, `SOURCES.md`, `AI_USE.md`, and `../docs/ROADMAP.md`.
