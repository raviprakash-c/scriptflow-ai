# Assessment Demo Recording Runbook

Use this checklist to record the real application. This document is a plan, not evidence that a recording or live demo already exists.

## Before recording
- [ ] Confirm the reviewer can access the intended repository and demo URL.
- [ ] Start the API and both frontends using the README instructions.
- [ ] Confirm the API health/readiness routes and `/docs` respond.
- [ ] Use only footage/audio whose commercial-use rights you can verify; do not present mock assets as cleared stock.
- [ ] Prepare one short script with 3–5 scenes and one deliberately invalid input.
- [ ] Close unrelated windows and hide secrets, tokens, personal files, and browser autofill.
- [ ] Start screen recording only after the app is ready. Keep the recording unedited and under 8 minutes.

## Suggested recording sequence (about 6–7 minutes)
1. **0:00–0:30 — Intro:** state the product goal and the current limits accurately.
2. **0:30–2:30 — Clean run:** submit a short script, inspect the scene plan, run a real render if providers and FFmpeg are available, then show the actual output file and its metadata. If the render cannot complete, record the failure; do not substitute a simulated preview.
3. **2:30–3:30 — Failure handling:** submit an invalid/empty input or demonstrate a provider failure, and show the structured error/retry behavior.
4. **3:30–4:30 — Tests:** run the documented test command and show the actual terminal output.
5. **4:30–5:45 — Design decision:** open the relevant code and explain one choice (for example, idempotency keys, output validation, or source/rights metadata).
6. **5:45–6:30 — Social Content Studio:** show creating/editing a draft, changing its status/calendar date, and exporting a content pack. Clearly say that external social publishing is not connected.
7. **6:30–7:00 — Wrap-up:** state what was demonstrated and what remains unverified.

## Evidence to preserve
- [ ] Original, unedited screen recording (maximum 8 minutes).
- [ ] Terminal logs for tests and the demo run, including failures.
- [ ] Every generated output, including failed/weak results, with its captions, timeline, and manifest when present.
- [ ] A test-pack index mapping report claims to filenames or links.
- [ ] Ten varied render cases with actual status, output validation, duration, elapsed time, and notes. Do not fill results before running the cases.
- [ ] Public demo URL, cold-start observation, and confirmation that the URL remains available through the review period.

## Important
- A green CI run proves the automated CI jobs passed; it does not prove a real provider call, a completed MP4 render, a hosted demo, or a successful social-media publish.
- Never claim an MP4 exists unless a valid rendered file exists.
- Never claim social content was published unless a real publishing operation succeeded.
- The official assessment workbook must be completed using the actual workbook sent by IncuBrix. This runbook is not a replacement.
