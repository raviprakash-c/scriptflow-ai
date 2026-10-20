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


def test_validate_av_sync_returns_alignment_metrics():
    result = render.validate_av_sync(
        {"start_time": "0.000", "duration": "12.000"},
        {"start_time": "0.080", "duration": "11.900"},
        12.0,
    )
    assert result["start_delta_seconds"] == 0.08
    assert result["duration_delta_seconds"] == 0.1


def test_validate_av_sync_rejects_offset_audio():
    with pytest.raises(ValueError, match="start times are out of sync"):
        render.validate_av_sync(
            {"start_time": "0", "duration": "10"},
            {"start_time": "0.5", "duration": "10"},
            10,
        )


def test_validate_av_sync_rejects_duration_mismatch():
    with pytest.raises(ValueError, match="durations are out of sync"):
        render.validate_av_sync(
            {"start_time": "0", "duration": "10"},
            {"start_time": "0", "duration": "7"},
            10,
        )


def test_visual_scan_reports_black_and_frozen_intervals(monkeypatch):
    monkeypatch.setattr(render.shutil, "which", lambda _name: "ffmpeg")
    monkeypatch.setattr(
        render.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0,
            stderr=(
                "[blackdetect] black_start:2.000 black_end:4.500 "
                "lavfi.freezedetect.freeze_start:5.0 "
                "lavfi.freezedetect.freeze_duration:3.0"
            ),
            stdout="",
        ),
    )
    warnings = render.inspect_visual_quality("example.mp4")
    assert any("black intervals" in warning for warning in warnings)
    assert any("frozen intervals" in warning for warning in warnings)


def test_visual_scan_failure_is_reported_as_warning(monkeypatch):
    monkeypatch.setattr(render.shutil, "which", lambda _name: "ffmpeg")
    monkeypatch.setattr(
        render.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=1, stderr="decoder error", stdout=""),
    )
    warnings = render.inspect_visual_quality("example.mp4")
    assert any("did not complete" in warning for warning in warnings)
