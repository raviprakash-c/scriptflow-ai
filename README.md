# ScriptFlow AI & Social Content Studio

This repository contains two independent frontends requested in the project initiation brief, plus the initial ScriptFlow PS3 backend engine.

## Apps

### ScriptFlow AI
`cd ScriptFlowAI/frontend`
```bash
npm install
npm run dev
npm run build
``
Workspace for script projects, scene plans, sample footage assignment, render checklist, history and draft metadata exports. Local sample visuals are not licensed stock footage; the frontend does not claim an MP4 exists until a real render is connected.

### Social Content Studio
`cd SocialContentStudio/frontend`
```bash
npm install
npm run dev
npm run build
``
Workspace for campaign briefs, sample content generation, editing and approvals, calendar planning, content library, workflow counts and CSV/JSON export. No social accounts are connected and no posts are automatically published.

### ScriptFlow engine
See [engine/README.md](engine/README.md) for the FastAPI service, API contract, Docker setup, test suite and known gaps.

## Configuration and demo data
Each frontend supports an optional `VITE_API_BASE_URL` value as an integration boundary. Do not place provider secrets in frontend environment variables. Both frontends use isolated localStorage adapters until real APIs are connected. Sample data is labelled and should not be represented as real production activity.

## Project status
This is a working development branch, not a claim that all assessment requirements are complete. Default engine TTS is silent timing audio, placeholder visuals are not commercially verified footage, engine job state is process-local, and no public demo is deployed. See [docs/ROADMAP.md](docs/ROADMAP.md) for the next execution sequence and acceptance checklist.
