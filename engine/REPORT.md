# ScriptFlow AI — Engineering report

## Approach
FastAPI with typed job requests, SQLite-persisted job records and idempotency keys, restart recovery for interrupted jobs, status/progress, scene planning, optional Pexels and Pixabay video providers, FFmpeg scene assembly, SRT/timeline/manifest outputs, tests, OpenAPI 3.1, Docker setup and a batch runner.

## Verified
- GitHub Actions builds both frontends and runs Python syntax compilation plus the engine test suite.
- Unit tests cover API input validation, idempotency replay/conflict, structured errors, durable job state, restart recovery, planner behavior, and mocked Pexels/Pixabay provider/fallback responses.
- Live provider calls are not verified because no real provider keys or local machine access were supplied.
- An earlier placeholder-only smoke run created an MP4 preview plus SRT, timeline and manifest files; this is not evidence of a live licensed-footage render.

## Known gaps
- Edge TTS needs outbound network access. If the provider fails, the job warns and may use silent timing audio. A silent output is not a narrated video.
- Pexels/Pixabay adapters preserve source, licence and attribution metadata when configured. Without keys or after failed searches/downloads, generated placeholder visuals are used and are not commercially verified.
- Stock media licences do not clear every depicted person, trademark, logo, or third-party work; rights review is required.
- Remote audio URL ingestion is not implemented; uploaded audio transcription requires the optional faster-whisper extra.
- SQLite persists metadata on a single host, but there is no distributed queue, shared database, object storage, authentication, rate limiting, signed callbacks, or full output-quality validation.
- Subtitle burn-in is not implemented. No public live demo or representative ten-input performance/quality/cost benchmark is available.

## Metrics
No production latency, cost per minute, human relevance score, audio-sync score, or success-rate metric is claimed.

## Remaining work
1. Test Edge TTS with live network; validate non-empty narration audio and probed duration.
2. Configure Pexels/Pixabay API keys and validate live search/download, contributor attribution and fallback behaviour.
3. Add shared durable jobs/queue, object storage, auth, signed callbacks, limits and a hosted demo.
4. Implement subtitle burn-in and validate codec, resolution, FPS, duration, audio sync, black/frozen frames and clip coverage.
5. Run at least ten varied inputs; preserve inputs, outputs, logs and measured results; complete the assessment workbook from that evidence.
