# ScriptFlow AI & Social Content Studio

ScriptFlow AI is an IncuBrix PS3 project for turning a script into a narrated video with captions. This repository also contains a separate Social Content Studio frontend and the video-generation API.

## Live demo

- **ScriptFlow AI frontend:** https://scriptflow-frontend.onrender.com
- **Backend API:** https://scriptflow-ai-soie.onrender.com
- **Backend health check:** https://scriptflow-ai-soie.onrender.com/health
- **Interactive API documentation:** https://scriptflow-ai-soie.onrender.com/docs
- **Full-project pull request:** https://github.com/raviprakash-c/scriptflow-ai/pull/3

The frontend and backend are deployed as separate Render services. Open the frontend to try the application; use the health check to confirm that the backend responds. A healthy backend does not by itself guarantee that a complete render will succeed, so test a generation before a presentation. Render free services may sleep, restart, or run out of resources during longer jobs. Generated files and SQLite job data on an ephemeral filesystem may not survive a service restart.

## Repository layout and branch

The full workspace is on branch `build/full-project-clean` and is proposed in Pull Request #3. To fetch it locally:

```powershell
git fetch origin
git switch build/full-project-clean
```

If the local branch does not exist yet:

```powershell
git switch --track origin/build/full-project-clean
```

The workspace includes `ScriptFlowAI/frontend`, `SocialContentStudio/frontend`, and `engine`.

## Run locally on Windows

From the repository root, run:

```powershell
.\scripts\dev.ps1
```

This opens separate terminal windows for both frontends and the API. To start only one component:

```powershell
.\scripts\dev.ps1 -App ScriptFlow
.\scripts\dev.ps1 -App SocialStudio
.\scripts\dev.ps1 -App Backend
```

Default local URLs:

- ScriptFlow AI: http://localhost:5173
- Social Content Studio: http://localhost:5174
- Engine API docs: http://localhost:8000/docs

### Start components manually

**ScriptFlow AI frontend**

```powershell
cd ScriptFlowAI/frontend
npm install
npm run dev
```

**Social Content Studio frontend**

```powershell
cd SocialContentStudio/frontend
npm install
npm run dev -- --port 5174
```

**Engine API**

```powershell
cd engine
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -e ".[test]"
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --port 8000 --env-file .env
```

For local narration with Edge TTS, install the project's dependencies including `edge-tts` and set `TTS_PROVIDER=edge-tts` in the backend process environment before starting Uvicorn. Do not commit secrets or local `.env` files. On macOS/Linux, activate the virtual environment with `source .venv/bin/activate` and copy the example file with `cp .env.example .env`.

## Main capabilities

- ScriptFlow AI frontend for script input, scene planning, render status, and video export.
- Backend API for creating and checking jobs and accessing generated output files.
- Text-to-speech narration when the Edge TTS provider is configured and reachable.
- Caption output when enabled for a generation.
- Separate Social Content Studio frontend for campaign briefs, labelled sample content, editing and approvals, calendar planning, library search, workflow counts, and CSV/JSON export.

Feature availability depends on the selected configuration and successful completion of a job. Verify the generated MP4, audio, captions, and manifest rather than assuming that a submitted job produced a complete result.

## Limitations and responsible use

- Demo or placeholder visuals are not the same as verified, licensed stock footage. Do not describe placeholder footage as real stock media.
- Commercial media rights have not been independently verified for every output. Review source licences and third-party rights before publishing.
- Social Content Studio does not connect social accounts or automatically publish posts.
- Both frontends use isolated localStorage adapters for some data until the relevant APIs are connected.
- The engine uses SQLite for single-host job metadata; it is not a distributed job queue. Ephemeral hosting storage can cause job history and output files to disappear after a restart.
- Render free services may sleep or restart, and long video renders may time out or exceed available memory.
- Never put provider API keys in frontend environment variables or commit secrets.

See `docs/ROADMAP.md` for further project notes. GitHub Actions builds both frontends and runs engine tests; a green CI build does not, by itself, prove that live provider calls or deployed video generation work.

## Pull request and CI

Full-project pull request: https://github.com/raviprakash-c/scriptflow-ai/pull/3
