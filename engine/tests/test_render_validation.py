import json
from types import SimpleNamespace

import pytest
import app.render as render


def test_validate_video_accepts_matching_mp4_metadata(tmp_path, monkeypatch):
    output = tmp_path / "render.mp4"
    output.write_bytes(b"x" * 2048)
    metadata = {
        "streams": [
            {"codec_type": "video", "codec_name": "h264", "width": 1920, "height": 1080},
            {"codec_type": "audio", "codec_name": "aac"},
        ],
        "format": {"duration": "12.0"},
    }
    monkeypatch.setattr(render.shutil, "which", lambda _: "ffprobe")
    monkeypatch.setattr(render, "run", lambda *args, **kwargs: SimpleNamespace(stdout=json.dumps(metadata)))
    result = render.validate_video(output, 1920, 1080, 12.0)
    assert result["codec"] == "h264"
    assert result["has_audio"] is True
    assert result["duration_seconds"] == 12.0


def test_validate_video_rejects_wrong_dimensions(tmp_path, monkeypatch):
    output = tmp_path / "render.mp4"
    output.write_bytes(b"x" * 2048)
    metadata = {
        "streams": [{"codec_type": "video", "codec_name": "h264", "width": 640, "height": 360},
                    {"codec_type": "audio", "codec_name": "aac"}],
        "format": {"duration": "12.0"},
    }
    monkeypatch.setattr(render.shutil, "which", lambda _: "ffprobe")
    monkeypatch.setattr(render, "run", lambda *args, **kwargs: SimpleNamespace(stdout=json.dumps(metadata)))
    with pytest.raises(ValueError, match="dimensions"):
        render.validate_video(output, 1920, 1080, 12.0)


def test_validate_video_rejects_missing_audio(tmp_path, monkeypatch):
    output = tmp_path / "render.mp4"
    output.write_bytes(b"x" * 2048)
    metadata = {
        "streams": [{"codec_type": "video", "codec_name": "h264", "width": 1920, "height": 1080}],
        "format": {"duration": "12.0"},
    }
    monkeypatch.setattr(render.shutil, "which", lambda _: "ffprobe")
    monkeypatch.setattr(render, "run", lambda *args, **kwargs: SimpleNamespace(stdout=json.dumps(metadata)))
    with pytest.raises(ValueError, match="no audio"):
        render.validate_video(output, 1920, 1080, 12.0)
