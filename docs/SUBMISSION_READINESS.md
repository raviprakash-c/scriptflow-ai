# IncuBrix Submission Readiness Checklist

Use this as a truthful evidence tracker, not as proof that a task has been completed. Tick an item only after you personally verify it and save the evidence. Keep evidence files outside the repository if they contain secrets or personal data.

## Shared repository / PR

- [x] Pull Request #3 contains the two frontend roots, engine, tests, CI, setup docs, OpenAPI contract and assessment notes.
- [x] Latest recorded CI run passed all three jobs on the PR head before this checklist commit: [run 39243365326](https://github.com/raviprakash-c/scriptflow-ai/actions/runs/39243365326).
- [ ] After this documentation commit, verify the new PR-head CI run is green.
- [ ] Locally run `git status` and confirm there are no uncommitted changes you need to preserve.
- [ ] Give `admin@incubrix.com` reviewer access to the repository, as required by the assessment email; verify the invite/permission is effective.
- [ ] Do not merge PR #3 just to make the branch visible. First ensure the submission branch has the correct changes and its checks pass.

## Local branch protection / Windows PowerShell

Run from `D:\scriptflow-ai`:

```powershell
git status --short --branch
git fetch origin
git switch build/full-project-clean
# Only if the local branch does not exist:
# git switch --track origin/build/full-project-clean
git pull --ff-only origin build/full-project-clean
git status --short --branch
git log -1 --oneline
```

Expected branch name: `build/full-project-clean`. If you have uncommitted work, stop before switching or pulling and save/commit it safely first. Do not delete or reset your stash.

## Software Engineer — PS3 ScriptFlow AI

- [ ] Obtain and use the correct official PS3 brief and workbook; do not use the Prompt-Based Video Editing Engine brief if the selected project is Script and Voiceover to B-roll Video Engine.
- [ ] Record the tested commit SHA, operating system, commands, provider configuration state and test date.
- [ ] Run both frontend production builds and engine tests locally; preserve full terminal output/logs.
- [ ] Complete and preserve at least ten varied render test cases. For each: input/script, intended aspect ratio/language, narration/provider state, footage source and licence/attribution, output file, ffprobe details, warnings, wall-clock time, failure/fallback behavior and evidence path.
- [ ] For every test that claims narration, listen to the rendered result and verify audible speech. Silent timing audio is a failure for narrated-video acceptance.
- [ ] Review footage source URLs, license information, attribution and depicted people/logos/trademarks before making commercial-use claims.
- [ ] Verify output can be downloaded and actually opens/plays. Never report placeholder visuals as licensed B-roll.
- [ ] Populate the official workbook row-by-row from measured results. Link every claim to an actual log, screenshot, output file, test or source; write “not measured” where necessary.
- [ ] Capture an unedited assessment demo video no longer than the stated 8-minute limit; show real workflows and honest failure/fallback states. Do not edit out errors in a way that misrepresents reliability.
- [ ] Deploy a public demo and test it from a separate browser/network. Confirm it stays available through result announcement; document any auth token securely if access is protected.
- [ ] Check required docs exist and are accurate: README, `engine/openapi.yaml`, `engine/REPORT.md`, `engine/SOURCES.md`, `engine/AI_USE.md`, plus any test pack named in the official brief.
- [ ] Submit using the final form: https://forms.gle/7BLzybcvbmyLXZjo6
- [ ] Confirm the Software Engineer start confirmation was submitted: https://forms.gle/iR5PB23Lhq5ioZLf8

## Growth Engineer — Option 2 Social Content Studio

- [ ] Obtain and use the correct official Option 2 Social Content Studio brief and workbook. The available Distribution: Long-Tail Destination Network brief does not match this selected option.
- [ ] Run the actual browser workflow and capture evidence for campaign creation, sample draft generation, editing, approval/rejection, calendar, library filtering, and CSV/JSON exports.
- [ ] Clearly label sample content as sample/demo content. Do not claim connected accounts, OAuth, scheduled delivery to platforms or actual publishing.
- [ ] Define a small, honest content experiment using the official brief's metrics; preserve the inputs, output samples, method, results and limitations. Do not invent reach, engagement, conversion or growth.
- [ ] Complete the official Growth workbook from measured evidence and screenshots, with every claim traced to evidence.
- [ ] Record a short walkthrough and submit the project/demo/repo evidence using the Growth assessment instructions and the official final submission form.

## Hosting plan — only mark deployed after smoke test

1. Keep provider keys and secrets in the hosting provider's server-side environment only; never put them in Vite/frontend variables or commit them.
2. Deploy the backend and both frontends. Configure frontend API URLs explicitly, allowed origins, persistent writable storage and FFmpeg/codec support. Verify provider network access and runtime limits.
3. Use a small non-sensitive test script. Verify API health/docs, create job, status polling, actual output download, audible narration, captions, dimensions/duration and logs.
4. Test from a clean browser/network and confirm no localhost URLs are embedded in the deployed frontend. Record demo URL, test date, deployed commit and known limitations.
5. Do not treat CI as hosted-demo evidence. Keep the demo available for the assessment period, and avoid exposing secrets in the video, logs or workbook.

## Evidence folder suggestion

Create a local folder not committed to Git, e.g. `submission-evidence/`, with:
- `00-commit-and-ci/` — PR head SHA and passing CI screenshots/logs.
- `01-local-build-tests/` — frontend build and pytest logs.
- `02-render-cases/` — each test input, output, metadata report and notes.
- `03-frontend-walkthroughs/` — dated screenshots and screen recordings.
- `04-live-demo/` — tested URL, smoke-test log and access notes (no secrets).
- `05-workbooks/` — official workbooks and backup copies.
- `06-final-submission/` — final video and submission receipt.

## Current status snapshot

- CI: latest recorded run passed all three jobs on commit `cb41dc5f70b4067d546a1e4059fab2634c1d2cf2`; rerun checks after later commits.
- Code-level implementation: present in PR #3.
- Live provider behavior, ten-input measured benchmark, public hosted demo and evidence-backed workbook: not verified / not complete at the time this checklist was written.
- Correct Growth Option 2 brief/workbook: still needed if not already available to the owner.
