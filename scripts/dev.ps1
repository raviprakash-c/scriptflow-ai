param(
    [ValidateSet("All", "ScriptFlow", "SocialStudio", "Backend")]
    [string]$App = "All"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

function Start-Frontend {
    param([string]$Name, [string]$RelativePath, [int]$Port)
    $directory = Join-Path $repoRoot $RelativePath
    if (-not (Test-Path (Join-Path $directory "package.json"))) {
        throw "Missing $Name frontend at '$directory'. Fetch and switch to build/full-project-clean first; see README.md."
    }
    $safeDirectory = $directory.Replace("'", "''")
    $command = "Set-Location -LiteralPath '$safeDirectory'; if (-not (Test-Path node_modules)) { npm install }; npm run dev -- --host 0.0.0.0 --port $Port"
    Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-Command", $command)
    Write-Host "$Name starting from $directory on port $Port"
}

function Start-Backend {
    $directory = Join-Path $repoRoot "engine"
    if (-not (Test-Path (Join-Path $directory "pyproject.toml"))) {
        throw "Missing engine/pyproject.toml. Fetch and switch to build/full-project-clean first."
    }
    if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
        throw "Python launcher 'py' was not found. Install an approved Python 3.11+ environment first."
    }
    $venvPython = Join-Path $directory ".venv\Scripts\python.exe"
    if (-not (Test-Path $venvPython)) {
        Push-Location $directory
        try { py -m venv .venv } finally { Pop-Location }
        if ($LASTEXITCODE -ne 0) { throw "Virtual environment creation failed." }
    }
    $envFile = Join-Path $directory ".env"
    if (-not (Test-Path $envFile)) {
        Copy-Item (Join-Path $directory ".env.example") $envFile
        Write-Host "Created engine/.env. Add provider keys there only if you have them."
    }
    $safeDirectory = $directory.Replace("'", "''")
    $command = "Set-Location -LiteralPath '$safeDirectory'; & '.\.venv\Scripts\python.exe' -m pip install -e '.[test]'; & '.\.venv\Scripts\python.exe' -m uvicorn app.main:app --reload --port 8000 --env-file .env"
    Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-Command", $command)
    Write-Host "Backend starting from $directory on port 8000"
}

switch ($App) {
    "ScriptFlow" { Start-Frontend "ScriptFlow AI" "ScriptFlowAI\frontend" 5173 }
    "SocialStudio" { Start-Frontend "Social Content Studio" "SocialContentStudio\frontend" 5174 }
    "Backend" { Start-Backend }
    "All" {
        Start-Frontend "ScriptFlow AI" "ScriptFlowAI\frontend" 5173
        Start-Frontend "Social Content Studio" "SocialContentStudio\frontend" 5174
        Start-Backend
        Write-Host "ScriptFlow: http://localhost:5173"
        Write-Host "Social Studio: http://localhost:5174"
        Write-Host "Engine API docs: http://localhost:8000/docs"
    }
}
