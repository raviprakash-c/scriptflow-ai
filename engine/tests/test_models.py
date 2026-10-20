import pytest
from pydantic import ValidationError
from app.models import JobRequest
def test_request_requires_exactly_one_input():
    with pytest.raises(ValidationError):JobRequest()
def test_request_rejects_multiple_modes():
    with pytest.raises(ValidationError):JobRequest(script="text",scenes=[{"text":"scene"}])
def test_scene_list_supports_visual_hint():
    req=JobRequest(scenes=[{"text":"Start here","visual_hint":"planning"}],aspect_ratios=["9:16"])
    assert req.scenes[0].visual_hint=="planning"
