import os
from dataclasses import dataclass
from pathlib import Path


def _int(name, default):
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "ScriptFlow AI")
    output_dir: Path = Path(os.getenv("OUTPUT_DIR", "./outputs")).resolve()
    job_db_path: Path = Path(os.getenv("JOB_DB_PATH", "./outputs/jobs.sqlite3")).resolve()
    audio_url_allowed_hosts: tuple = tuple(x.strip().lower() for x in os.getenv("AUDIO_URL_ALLOWED_HOSTS", "").split(",") if x.strip())
    max_audio_seconds: int = _int("MAX_AUDIO_SECONDS", 600)
    max_upload_mb: int = _int("MAX_UPLOAD_MB", 100)
    max_stock_clip_mb: int = _int("MAX_STOCK_CLIP_MB", 80)
    default_fps: int = _int("OUTPUT_FPS", 30)
    default_voice: str = os.getenv("DEFAULT_VOICE", "en-IN-female")
    tts_provider: str = os.getenv("TTS_PROVIDER", "mock")
    cors_origins: tuple = tuple(
        x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if x.strip()
    )


settings = Settings()
