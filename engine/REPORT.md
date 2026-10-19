# ScriptFlow AI — Engineering report (working draft)

## Approach
FastAPI with typed request validation, a process-local job store, idempotency keys, job status/progress, a scene planner, a mock footage adapter, FFmpeg placeholder rendering, SRT/timeline/manifest outputs, tests, OpenAPI spec and batch runner.

## Tested locally
Python source compilation passed. The local pytest suite passed (see the development-session result). A smoke request created an MP4 placeholder preview and SRT, timeline and manifest outputs. Regenerate and preserve test results from the final revision before submission.

## Known gaps
- Generated placeholder visuals are not commercially verified footage; `commercial_use=false`. Must-have #3 is not met.
- Default TTS is silent timing audio; script narration is not produced unless a supported TTS provider is configured. Must-have #1 is not met by default.
- Audio transcription requires optional faster-whisper, a model, and FFmpeg/ffprobe. Remote URL ingestion is not implemented; uploaded audio is supported.
- Process-local job state is not durable. No database, distributed queue, MinIO/S3, signed callbacks, source fallback between two real providers, subtitle burn-in, clip-swap rerender, independent relevance scoring, Hindi/Tamil QA or public live demo yet.
- No production performance, human relevance or cost benchmarks are claimed.

## Metrics
Not measured on representative hardware or a ten-input suite. Do not infer costs or relevance from the generated preview.

## Next steps
1. Configure a commercially licensed stock source plus fallback; preserve licence and attribution from provider responses.
2. Configure TTS and transcription, then test English, Hindi and Tamil.
3. Add durable jobs, storage, signed callbacks, rate limiting, and a hosted demo.
4. Add validation for codec, resolution, FPS, black/frozen frames and audio sync; implement burned captions.
5. Run ten varied inputs, preserve all successful and failed outputs/logs, collect reviewer scores, then complete the assessment workbook accurately.
