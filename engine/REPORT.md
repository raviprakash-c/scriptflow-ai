# ScriptFlow AI — Engineering report

## Approach
FastAPI with typed job requests, SQLite-persisted job records and idempotency keys, restart recovery for interrupted jobs, status/progress, scene planning, optional Pexels and Pixabay video providers, FFmpeg scene assembly, SRT/timeline/manifest outputs, tests, OpenAPI 3.1, Docker setup and a batch runner.

## Verified in repository / CI
- The latest recorded GitHub Actions run for PR #3 is [Build and test run 39243365326](https://github.com/raviprakash-c/scriptflow-ai/actions/runs/39243365326), on commit `cb41dc5f70b4067d546a1e4059fab2634c1d2cf2`.
- All three jobs succeeded: engine tests (dependency install, Python compile, pytest), ScriptFlow frontend production build, and Social Content Studio frontend production build.
- Automated tests cover API input validation, idempotency replay/conflict, structured errors, durable job state, restart recovery, planner behavior, mocked Pexels/Pixabay provider/fallback responses, remote audio safeguards, SRT/captions and render-validation behavior.
- Code implements SRT subtitle burn-in, ffprobe metadata checks (including H.264, dimensions, audio stream, duration and minimum file size), stream-start/duration synchronization checks, and FFmpeg black/frozen-frame diagnostics that produce warnings for human review.
- CI proves these automated checks pass in its test environment. It does not prove real providers, live narrated media, stock licensing, or a public deployment works.

## Known gaps and risk boundaries
- Live Edge TTS and Pexels/Pixabay search/download have not been verified with real credentials in the assessment environment. The configured fallback may create silent timing audio or placeholder visuals; neither should be presented as proof of a narrated, licensed-footage render.
- Stock media source/licence/attribution metadata can be preserved, but it does not clear every depicted person, trademark, logo, or third-party work. Review the exact assets and terms before commercial use.
- Remote audio ingestion applies an explicit HTTPS host allowlist, public-address DNS checks, disabled redirects, and streamed size/content-type limits. DNS-rebinding resistance at the transport layer and deployment egress controls still need hardening.
- SQLite provides single-host persistence only. There is no distributed queue, shared database, object storage, authentication/authorization, rate limiting, signed callbacks, or secured production artifact delivery.
- Black/frozen-frame diagnostics are heuristics and warnings, not a guarantee of visual quality. Human review is still required.
- Social Content Studio is a local demo workflow; it does not connect social accounts or publish posts.
- No public live demo or evidence-backed ten-input performance/quality/cost benchmark is available yet.

## Metrics
No production latency, cost per minute, human relevance score, audio-sync score, or success-rate metric is claimed. Record measurements only after running the defined test set and preserving the raw evidence.

## Remaining work — submission-critical
1. Run and record manual journeys for both frontends; capture dated screenshots or screen recording and note exact build/commit.
2. Run at least ten varied end-to-end video inputs; save input, output, logs, provider/source/licence/attribution metadata, ffprobe results, observed warnings and measured duration/cost where available. Mark unavailable values as not measured; do not estimate them.
3. Test live narration and stock providers only after valid backend-only credentials and outbound network access are configured. Confirm the final file contains audible narration rather than silent timing audio.
4. Deploy and smoke-test a public demo, keep it available through assessment results, and share access instructions or a token only if needed. Do not claim hosting is live until tested from a separate browser/network.
5. Complete the official assessment workbook from actual results/screenshots; cite evidence for every claim. Confirm workbook rows and headings against the correct PS3 assessment brief.
6. Keep the Growth Engineer Option 2 Social Content Studio submission evidence separate and aligned to its official brief. Do not claim OAuth or real publishing.
7. Before submission, verify repository reviewer access, required documents, demo/video URL, workbook and final form; retain a copy of the exact submitted materials.

## Security / production work beyond the immediate evidence pass
1. Add shared database/queue, storage lifecycle, retry/cancel semantics, authentication, authorization, rate limiting and secured artifact delivery.
2. Harden remote audio against DNS rebinding and add deployment egress controls; strengthen uploaded-file signature validation.
3. Expand fixture-backed acceptance tests for output quality and uncovered scene gaps.
4. Add Social Studio persistence and provider OAuth only when credentials and authorization are available, with preview/confirmation and idempotent publishing.
