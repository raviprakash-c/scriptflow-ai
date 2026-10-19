# Full Project Completion Roadmap

This roadmap follows the original Project-Initiation brief. It separates what is implemented from what still needs verification. Do not mark an item complete because a screen exists; acceptance means the user journey works and the behavior is tested.

## Current branch
- `build/two-product-frontends` contains two independent React + TypeScript + Vite frontend roots and the initial API-engine branch.
- Both frontends use typed local demo services backed by browser localStorage.
- Social sample content is labelled sample; ScriptFlow sample visuals and unrendered MP4 status are explicit.
- The local GitHub integration is the source of truth for commits. Run the build workflow before merging; this coding environment cannot directly access npm/GitHub over shell networking.

## Current validation status (2026-10-19)
- [x] GitHub Actions production build: `ScriptFlowAI/frontend` passed.
- [x] GitHub Actions production build: `SocialContentStudio/frontend` passed.
- [x] Python syntax compilation and all 20 engine tests passed in CI.
- [x] Optional Pexels/Pixabay adapters and mocked API/fallback tests added; real API keys are still needed for live validation.
- Build workflow run: https://github.com/raviprakash-c/scriptflow-ai/actions/runs/39214536310
- [ ] Browser-based manual user-journey testing is still required.
- [ ] Engine/provider integration and ten-input production testing remain incomplete.

## Phase 1 — Build and validate both frontends (highest immediate priority)
1. Run `cd ScriptFlowAI/frontend && npm install && npm run build`.
2. Run `cd SocialContentStudio/frontend && npm install && npm run build`.
3. Fix TypeScript/build failures before adding more features.
4. Test the ScriptFlow journey: create project → edit script → review scenes → assign sample visuals → review render checklist → export timeline/manifest/SRT. Confirm no UI claims an MP4 exists.
5. Test the Social Studio journey: create campaign → generate local sample drafts → edit → approve/reject → plan a date → filter library/calendar → export CSV and JSON.
6. Check desktop, tablet, mobile, keyboard navigation, labels, empty states and confirmation prompts.
7. Add CI build checks and record actual results in this document.

## Phase 2 — ScriptFlow engine: real outputs
1. Run Edge TTS with the configured voice on live network; validate non-empty narration audio and probed duration. A silent-audio fallback must never be represented as a narrated render.
2. Configure a real Pexels API key, validate live search/download and visible attribution, then add a second commercial source/fallback. The engine now uses downloaded MP4 clips when Pexels returns them; placeholder fallback remains explicitly unverified.
3. Persist source URL, provider asset ID, license terms, attribution, commercial-use status and retrieval time per clip. Reject unverified sources for commercial mode.
4. Implement remote audio URL handling with SSRF protection (allow-list protocols, block private/link-local IPs, limit redirects/bytes/time), as well as upload size/type/duration validation.
5. Implement caption burn-in, SRT export, aspect ratios, transitions, volume controls, and output validation (ffprobe metadata, audio/video duration, dimensions, FPS, black/frozen-frame checks).
6. Move jobs from in-memory state to a durable database and queue. Add safe retries, cancellation, concurrency limits, rate limiting, timeouts and cleanup of temporary files.
7. Add object storage or persistent artifact storage, short-lived download URLs, retention policies, and a callback/webhook design with signatures if required by the assessment.
8. Add job progress that reflects real stages, stable job IDs, structured logs, correlation IDs, and retryable vs terminal errors.
9. Run at least ten varied inputs (script/audio, short/long, 16:9/9:16, multi-language). Save every input, job status, output, logs, and measured runtime. Do not invent costs or quality scores.

## Phase 3 — Social Content Studio: integration-ready workflow
1. Keep local storage isolated behind the existing service interface; add a backend API adapter selected by configuration.
2. Add persistent server-side campaigns/posts, ownership and validation, and audit history for edits and approvals.
3. If AI generation is added, keep prompts/templates on the backend, validate structured output, apply platform character limits, and clearly distinguish generated from user-edited content.
4. Add real analytics only after OAuth/account connection and verified provider metrics are implemented.
5. Implement real publishing/scheduling only with explicit account authorization, preview, confirmation, timezone handling, provider success response, and retry/idempotency handling. Never fake published status.
6. Add CSV/JSON export tests, import validation if added, duplicate detection, and date/timezone tests.

## Phase 4 — Shared production readiness
1. Add CI for both frontends and the engine tests; pin dependency versions and commit lockfiles.
2. Add API contract tests, auth/authorization, secret management, CORS restrictions, rate limits, input validation, dependency scanning, and secure file delivery.
3. Add accessibility review (keyboard, focus, labels, contrast), responsive viewport checks, and error-boundary coverage.
4. Add deployment configuration and health checks; deploy only after secrets and persistence are configured.
5. Update the Excel submission workbook only with real evidence. Attach test logs, example outputs, screenshots, a working demo URL if available, source/licence records, and measured metrics.
6. Re-read every assessment must-have and mark pass/partial/fail with evidence. Keep the pull request unmerged if critical tests fail.

## Acceptance checklist
- [x] Both apps install and build successfully in GitHub Actions.
- [ ] Every required screen is navigable and all primary controls work.
- [ ] Core ScriptFlow journey is completed without claiming fake render results.
- [ ] Core Social Studio journey is completed and exports are valid.
- [ ] Sample/demo data and integrations are clearly identified.
- [ ] Mobile and keyboard flows are usable.
- [x] Backend API contract is documented; 18 engine tests pass in GitHub Actions.
- [ ] Live TTS produces real narration; video includes real licensed footage from configured providers.
- [ ] Media rights are preserved and checked for every asset.
- [ ] Durable jobs/storage, error handling and output validation are implemented.
- [ ] Ten representative test runs have evidence and honest metrics.
- [ ] Deployment and submission workbook are backed by verified evidence.
