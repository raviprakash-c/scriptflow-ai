from app.render import build_srt
def test_srt_timing_and_caption_text():
    result=build_srt([{"text":"Save money today.","start":0.0,"end":4.0},{"text":"Track spending.","start":4.0,"end":7.0}])
    assert result.startswith("1\n00:00:00,000 -->")
    assert "Track spending." in result
