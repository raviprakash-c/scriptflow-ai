import socket
from types import SimpleNamespace

import pytest
import app.render as render


def _public_dns(_host, _port, type=None):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]


def test_remote_audio_url_requires_https_allowlisted_host(monkeypatch):
    monkeypatch.setattr(render, "settings", SimpleNamespace(audio_url_allowed_hosts=("media.example",)))
    monkeypatch.setattr(render.socket, "getaddrinfo", _public_dns)
    assert render.validate_remote_audio_url("https://media.example/audio/demo.mp3") == ("media.example", ".mp3")
    with pytest.raises(ValueError, match="HTTPS"):
        render.validate_remote_audio_url("http://media.example/audio/demo.mp3")
    with pytest.raises(ValueError, match="allow-listed"):
        render.validate_remote_audio_url("https://other.example/audio/demo.mp3")


def test_remote_audio_url_rejects_private_dns_results(monkeypatch):
    monkeypatch.setattr(render, "settings", SimpleNamespace(audio_url_allowed_hosts=("media.example",)))
    monkeypatch.setattr(
        render.socket,
        "getaddrinfo",
        lambda *_args, **_kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))],
    )
    with pytest.raises(ValueError, match="non-public"):
        render.validate_remote_audio_url("https://media.example/audio/demo.mp3")


def test_remote_audio_download_rejects_redirects_and_removes_partial_file(tmp_path, monkeypatch):
    monkeypatch.setattr(render, "settings", SimpleNamespace(audio_url_allowed_hosts=("media.example",), max_upload_mb=1))
    monkeypatch.setattr(render.socket, "getaddrinfo", _public_dns)

    class RedirectResponse:
        status_code = 302
        headers = {"location": "http://127.0.0.1/private.mp3"}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def raise_for_status(self):
            return None

    monkeypatch.setattr(render.httpx, "stream", lambda *_args, **_kwargs: RedirectResponse())
    with pytest.raises(ValueError, match="redirects are not allowed"):
        render.download_remote_audio("https://media.example/audio/demo.mp3", tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_remote_audio_download_streams_with_size_limit(tmp_path, monkeypatch):
    monkeypatch.setattr(render, "settings", SimpleNamespace(audio_url_allowed_hosts=("media.example",), max_upload_mb=1))
    monkeypatch.setattr(render.socket, "getaddrinfo", _public_dns)

    class AudioResponse:
        status_code = 200
        headers = {"content-type": "audio/mpeg", "content-length": "1024"}

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def raise_for_status(self):
            return None

        def iter_bytes(self, _chunk_size):
            yield b"a" * 1024

    monkeypatch.setattr(render.httpx, "stream", lambda *_args, **_kwargs: AudioResponse())
    path = render.download_remote_audio("https://media.example/audio/demo.mp3", tmp_path)
    assert path.suffix == ".mp3"
    assert path.stat().st_size == 1024
