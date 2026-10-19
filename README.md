# ScriptFlow AI & Social Content Studio

This repository contains two independent frontends and the ScriptFlow AI video-generation API.

## First: get the correct project branch

The full workspace currently lives on branch build/full-project-clean and is proposed in Pull Request #3. If your local repository only has a folder named frontend, it is likely on an older revision. From the repository root, run:

    git fetch origin
    git switch build/full-project-clean

If Git says the local branch does not exist, run:

    git switch --track origin/build/full-project-clean

After switching, these directories must exist: ScriptFlowAI/frontend, SocialContentStudio/frontend, and engine. If the branch is not available remotely, open the pull request linked below and check it out from GitHub.

## Start everything on Windows

Open PowerShell at the repository root and run:

    .\scripts\dev.ps1

This opens separate terminal windows for both frontends and the API. To start only one component:

    .\scripts\dev.ps1 -App ScriptFlow
    .\scripts\dev.ps1 -App SocialStudio
    .\scripts\dev.ps1 -App Backend

The default local URLs are:
- ScriptFlow AI: http://localhost:5173
- Social Content Studio: http://localhost:5174
- Engine API docs: http://localhost:8000/docs

The script installs frontend dependencies when node_modules is missing. For the engine, it creates a local Python virtual environment, copies engine/.env.example to engine/.env if needed, installs the package and tests, then starts Uvicorn. If a managed Windows device blocks Python/pip through Application Control, use an approved Python environment or ask the administrator; do not try to bypass the policy.

## Start components manually

### ScriptFlow AI

    cd ScriptFlowAI/frontend
    npm install
    npm run dev

### Social Content Studio

    cd SocialContentStudio/frontend
    npm install
    npm run dev -- --port 5174

### Engine API

    cd engine
    py -m venv .venv
    .venv\Scripts\Activate.ps1
    py -m pip install -e ".[test]"
    Copy-Item .env.example .env
    python -m uvicorn app.main:app --reload --port 8000 --env-file .env

On macOS/Linux, activate with source .venv/bin/activate and copy with cp .env.example .env.

## Product boundaries

ScriptFlow is a workspace for projects, scene plans, footage assignment, render status and exports. Local demo visuals are not licensed stock footage; the frontend must not claim an MP4 exists until a real render has completed.

Social Content Studio supports campaign briefs, labelled sample content, editing and approvals, calendar planning, library search, workflow counts and CSV/JSON export. No social accounts are connected and no posts are automatically published.

Both frontends use isolated localStorage adapters until real APIs are connected. Never place provider API keys in frontend environment variables. The engine uses SQLite for single-host job metadata, but it is not a distributed queue. Live TTS, stock footage, media rights, production security, hosting and the assessment workbook still require evidence. See docs/ROADMAP.md.

## Pull request and CI

Full-project pull request: https://github.com/raviprakash-c/scriptflow-ai/pull/3

GitHub Actions builds both frontends and runs engine tests. A green CI build is not evidence of live provider calls or a deployed public demo.
