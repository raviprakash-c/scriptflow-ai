import os
from dataclasses import dataclass
from pathlib import Path
def _int(name, default):
    try: return int(os.getenv(name, str(default)))
    except ValueError: return default
@dataclass(frozen=True)
class Settings:
    app_name: str=os.getenv("APP_NAME","ScriptFlow AI")
    output_dir: Path=Path(os.getenv("OUTPUT_DIR","./outputs")).resolve()
    max_audio_seconds: int=_int("MAX_AUDIO_SECONDS",600)
    max_upload_mb: int=_int("MAX_UPLOAD_MB",100)
    default_fps: int=_int("OUTPUT_FPS",30)
    default_voice: str=os.getenv("DEFAULT_VOICE","en-IN-female")
    tts_provider: str=os.getenv("TTS_PROVIDER","mock")
    cors_origins: tuple=tuple(x.strip() for x in os.getenv("CORS_ORIGINS","http://localhost:5173").split(",") if x.strip())
settings=Settings()
