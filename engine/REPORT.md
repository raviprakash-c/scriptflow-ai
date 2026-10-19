# ScriptFlow AI — Engineering report (working draft)

## Approach
FastAPI with typed job requests, a process-local job store, idempotency keys, job status/progress, scene planning, optional Pexels and Pixabay video providers, FFmpeg scene assembly, SRT/timeline/manifest outputs, tests, OpenAPI 3.1, Docker setup and a batch runner.

## Verified in this workspace
- GitHub Actions ran `python -m compileall -q app scripts tests` successfully and passed all 18 pytest tests before the latest Pixabay fallback tests were added; rerun CI for the current revision.
- GitHub Actions production builds passed for both frontends.
- The Pexels and Pixabay adapters, including the second-provider fallback, have mocked-response unit tests; live key/download behavior is not verified.
- A smoke run on the earlier placeholder revision created an MP4 preview plus SRT, timeline and manifest files.

## Known gaps
- Edge TTS is included as a backend dependency and can be enabled with `TTS_PROVIDER=edge-tts`; it needs outbound network access. Live speech generation still needs a manual test. If it fails, the worker warns and may use silent timing audio. A silent output is not a narrated video.
- Pexels and Pixabay adapters download MP4 footage and preserve source/licence/attribution metadata when configured with API keys. Without keys or after failed searches/downloads, generated placeholder visuals are used and remain not commercially verified.
- Stock media licences do not clear every depicted person, trademark, logo, or third-party work; rights review is required.
- Remote audio URL ingestion is not implemented; uploaded audio transcription requires the optional faster-whisper extra.
- Process-local job state is not durable. No database, distributed queue, object storage, signed callbacks, rate limiting, user authentication, subtitle burn-in, clip-swap rerender, or full output quality validation is configured.
- No public live demo or representative ten-input performance/quality/cost benchmark is available.

## Metrics
No production latency, cost per minute, human relevance score, audio-sync score, or success-rate metric is claimed.

## Next steps
1. Test Edge TTS with live network; validate non-empty narration audio and probed duration.
2. Configure Pexels/Pixabay API keys and validate live search/download, contributor attribution and fallback behaviour.
3. Add durable jobs, object storage, auth, signed callbacks, limits and a hosted demo.
4. Add subtitle burn-in and validate codec, resolution, FPS, duration, audio sync, black/frozen frames and clip coverage.
5. Run at least ten varied inputs; preserve inputs, outputs, logs and measured results; complete the assessment workbook from that evidence.
