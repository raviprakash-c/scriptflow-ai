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

from app.providers import PixabayFootageProvider, CompositeFootageProvider

class FakePixabayResponse:
    def raise_for_status(self):
        return None
    def json(self):
        return {"hits":[{"id":456,"pageURL":"https://pixabay.com/videos/sample-456/","user":"Another Contributor","videos":{"medium":{"url":"https://cdn.pixabay.com/videos/sample.mp4","width":1920,"height":1080}}}]}

def test_pixabay_candidate_preserves_source_and_rights(monkeypatch):
    monkeypatch.setattr("app.providers.httpx.get",lambda *args,**kwargs: FakePixabayResponse())
    asset,score,reason=PixabayFootageProvider("test-key").search("team collaboration")
    assert asset.source=="Pixabay"
    assert asset.source_url.startswith("https://pixabay.com/")
    assert asset.download_url.endswith(".mp4")
    assert asset.license=="Pixabay Content License"
    assert "Another Contributor" in asset.attribution
    assert asset.commercial_use is True
    assert 0<=score<=1 and reason

class FakeEmptyPexelsResponse:
    def raise_for_status(self):
        return None
    def json(self):
        return {"videos":[]}

def test_composite_uses_second_provider_when_first_has_no_clip(monkeypatch):
    responses=[FakeEmptyPexelsResponse(),FakePixabayResponse()]
    monkeypatch.setattr("app.providers.httpx.get",lambda *args,**kwargs: responses.pop(0))
    composite=CompositeFootageProvider([PexelsFootageProvider("pexels-key"),PixabayFootageProvider("pixabay-key")])
    asset,_,_=composite.search("team collaboration")
    assert asset.source=="Pixabay"
