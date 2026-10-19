# Full Project Completion Roadmap

This roadmap follows the original Project-Initiation brief. A screen is not complete until the user journey works and the behavior is tested.

## Current branch and validation
- Consolidated implementation branch: build/full-project-clean. Follow-up completion work is developed separately and proposed through a pull request.
- Both frontends use typed local demo services backed by browser localStorage. Social sample content is labelled sample; ScriptFlow placeholder visuals and unrendered MP4 status are explicit.
- GitHub Actions production builds for both frontends and the engine test suite passed on the consolidated revision. The follow-up changes must pass CI before they are treated as verified.
- Live TTS, live stock downloads, browser-based manual journeys, and production deployment cannot be certified without provider credentials and runtime evidence.

## Completed implementation (code-level)
- [x] Two separate React + TypeScript + Vite frontend roots.
- [x] ScriptFlow project creation, scene planning/editing, footage assignment, render status integration, export/history/settings screens.
- [x] Social Content Studio campaign, draft editing/approval, calendar, library and CSV/JSON exports.
- [x] FastAPI job API, scene planner, MP4 assembly, SRT/timeline/manifest outputs, optional Edge TTS and Pexels/Pixabay adapters.
- [x] CI build/test workflow and mocked provider tests.
- [x] SQLite job and idempotency persistence for single-host use, plus restart recovery for interrupted jobs (follow-up branch; pending CI).
- [ ] Durable distributed queue/shared database and object storage.
- [ ] Remote audio URL ingestion with SSRF protection.
- [x] SRT subtitle burn-in and basic ffprobe MP4 metadata validation (follow-up branch; pending CI).
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
2. Implement remote audio ingestion safely (allow-list protocols, block private/link-local IPs, limit redirects/bytes/time) and strengthen upload validation. Extend output validation with black/frozen-frame and audio/video sync checks.
3. Validate outputs with ffprobe (codec, dimensions, FPS, duration, audio/video sync), and detect black/frozen frames and uncovered scene gaps.
4. Add Social Studio backend persistence and provider OAuth only when credentials and authorization are available; use explicit preview/confirmation and idempotent publishing.
5. Deploy a public demo after secrets, persistence, monitoring and security checks are configured.

The pull request should remain unmerged if CI fails or critical tests fail. A green build is not evidence of live-provider or deployment acceptance.
