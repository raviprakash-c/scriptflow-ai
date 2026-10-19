from app.providers import PexelsFootageProvider, get_footage_provider

class FakeResponse:
    def raise_for_status(self):
        return None
    def json(self):
        return {"videos":[{"id":123,"url":"https://www.pexels.com/video/sample-123/","user":{"name":"A Contributor"},"video_files":[{"file_type":"video/mp4","link":"https://videos.pexels.com/video-files/sample.mp4","width":1280,"height":720}]}]}

def test_pexels_candidate_preserves_source_and_rights(monkeypatch):
    monkeypatch.setattr("app.providers.httpx.get",lambda *args,**kwargs: FakeResponse())
    asset,score,reason=PexelsFootageProvider("test-key").search("team collaboration")
    assert asset.source=="Pexels"
    assert asset.source_url.startswith("https://www.pexels.com/")
    assert asset.download_url.endswith(".mp4")
    assert asset.license=="Pexels License"
    assert "A Contributor" in asset.attribution
    assert asset.commercial_use is True
    assert 0<=score<=1 and reason

def test_pexels_provider_requires_key(monkeypatch):
    monkeypatch.setenv("FOOTAGE_PROVIDER","pexels")
    monkeypatch.delenv("PEXELS_API_KEY",raising=False)
    assert get_footage_provider().name=="mock"
