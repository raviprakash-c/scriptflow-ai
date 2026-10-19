# ScriptFlow AI — Engineering report (working draft)

## Approach
FastAPI with typed job requests, a process-local job store, idempotency keys, job status/progress, scene planning, a local placeholder provider, an optional Pexels video provider, FFmpeg scene assembly, SRT/timeline/manifest outputs, tests, OpenAPI 3.1, Docker setup and a batch runner.

## Verified in this workspace
- GitHub Actions ran `python -m compileall -q app scripts tests` successfully and passed all 18 pytest tests after the Pexels integration.
- Python syntax compilation passed for the earlier engine revision.
- A smoke run created an MP4 placeholder preview plus SRT, timeline and manifest files.
- GitHub Actions production builds passed for both frontends.
- The Pexels provider now has mocked-response unit tests; it has not been exercised with a live API key in this environment.

## Known gaps
- Edge TTS is included as a backend dependency and can be enabled with `TTS_PROVIDER=edge-tts`; it needs outbound network access. Live speech generation still needs a manual test. If it fails, the worker warns and may use silent timing audio. Inspect the manifest; a silent output is not a narrated video.
- The Pexels adapter downloads MP4 footage and preserves source/license/attribution metadata when `PEXELS_API_KEY` is configured. Its mocked API unit test passes; live key/download behavior is not verified. Without a key or after a failed search/download, generated placeholder visuals are used and remain not commercially verified.
- Pexels commercial-use licensing does not clear every depicted person, trademark, logo, or third-party work; rights review is required.
- Remote audio URL ingestion is not implemented; uploaded audio transcription requires the optional faster-whisper extra.
- Process-local job state is not durable. No database, distributed queue, object storage, signed callbacks, rate limiting, user authentication, subtitle burn-in, clip-swap rerender, or full output quality validation is configured.
- No public live demo or representative ten-input performance/quality/cost benchmark is available.

## Metrics
No production latency, cost per minute, human relevance score, audio-sync score, or success-rate metric is claimed.

## Next steps
1. Configure a real Pexels key and test actual footage downloads, attribution and fallback behaviour.
2. Run Edge TTS with English, Hindi and Tamil sample scripts and inspect the generated audio.
3. Add durable jobs, object storage, auth, signed callbacks, limits and a hosted demo.
4. Add subtitle burn-in and validate codec, resolution, FPS, duration, audio sync, black/frozen frames and clip coverage.
5. Run at least ten varied inputs; preserve inputs, outputs, logs and measured results; complete the assessment workbook from that evidence.
