# Full Project Completion Roadmap

This roadmap follows the original Project-Initiation brief. A screen is not complete until the user journey works and the behavior is tested.

## Current branch and validation
- Current working branch: build/full-project-clean; Pull Request #3 remains open and unmerged. Latest verified code commit before this documentation update: a425b3c459ad55880894599cd114c41526a20e9c.
- Both frontends use typed local demo services backed by browser localStorage. Social sample content is labelled sample; ScriptFlow placeholder visuals and unrendered MP4 status are explicit.
- Latest code revision passed GitHub Actions: https://github.com/raviprakash-c/scriptflow-ai/actions/runs/39218090630. Both frontend production builds, Python syntax compilation, and 31 engine tests passed.
- Live TTS, live stock downloads, browser-based manual journeys, and production deployment cannot be certified without provider credentials and runtime evidence.

## Completed implementation (code-level)
- [x] Two separate React + TypeScript + Vite frontend roots.
- [x] ScriptFlow project creation, scene planning/editing, footage assignment, render status integration, export/history/settings screens.
- [x] Social Content Studio campaign, draft editing/approval, calendar, library and CSV/JSON exports.
- [x] FastAPI job API, scene planner, MP4 assembly, SRT/timeline/manifest outputs, optional Edge TTS and Pexels/Pixabay adapters.
- [x] CI build/test workflow and mocked provider tests.
- [x] SQLite job and idempotency persistence for single-host use, restart recovery for interrupted jobs, and idempotent backend retries.
- [ ] Durable distributed queue/shared database and object storage.
- [x] HTTPS remote audio ingestion with explicit host allowlist, public DNS checks, redirects disabled, and streamed size/content-type limits.
- [ ] Harden remote audio against DNS rebinding with pinned transport-level resolution and deployment egress controls.
- [x] SRT subtitle burn-in and ffprobe MP4 validation (H.264, dimensions, audio stream, duration, minimum file size, stream-start/duration sync checks, black/frozen-frame diagnostics).
- [ ] Authentication/authorization, rate limiting, signed callbacks, and secured artifact delivery.
- [ ] Social platform OAuth and actual publishing; do not fake connected accounts or published status.
- [ ] Ten representative end-to-end render runs with evidence and measured metrics.
- [ ] Hosted demo and assessment workbook populated from verified evidence.

## Required local validation
1. Build each frontend from its own directory: npm install, then npm run build.
2. Run engine tests from engine: python -m pip install -e ".[test]", then python -m pytest -q.
3. Test ScriptFlow: create project → edit script → review scenes → assign sample visuals → start render → check real job status → download actual artifacts. Never claim an MP4 exists when only local demo data is present.
4. Test Social Studio: create campaign → generate labelled sample drafts → edit → approve/reject → schedule a draft date → filter library/calendar → export CSV and JSON.
5. Check desktop/tablet/mobile, keyboard navigation, labels, empty states, errors and confirmation prompts.
6. Configure provider keys only in the backend environment; test live TTS and stock footage, inspect all license/source/attribution metadata, and manually review depicted people/logos/trademarks.
7. Run ten varied inputs (short/long scripts, audio, multiple aspect ratios and languages); save inputs, outputs, logs and measured metrics. Do not invent costs or quality scores.
8. Complete the assessment workbook only from actual evidence and screenshots.

## Remaining production work
1. Add shared database/queue, storage lifecycle, retry/cancel semantics, authentication, authorization, rate limiting and secured artifact delivery.
2. Harden remote audio against DNS rebinding and add deployment egress controls; strengthen uploaded-file signature validation. Extend output validation with automated quality thresholds and fixture-backed real-media acceptance tests; current black/frozen-frame findings are warnings for human review.
3. Validate outputs with ffprobe (codec, dimensions, FPS, duration, audio/video sync), review black/frozen-frame warnings, and detect uncovered scene gaps.
4. Add Social Studio backend persistence and provider OAuth only when credentials and authorization are available; use explicit preview/confirmation and idempotent publishing.
5. Deploy a public demo after secrets, persistence, monitoring and security checks are configured.

The pull request should remain unmerged if CI fails or critical tests fail. A green build is not evidence of live-provider or deployment acceptance.
