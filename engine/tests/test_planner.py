from app.planner import split_script,plan_scenes
def test_sentence_splitting():
    assert split_script("Save money. Track spending! Start now.")==["Save money.","Track spending!","Start now."]
def test_planned_duration_is_covered():
    scenes=plan_scenes([("a sentence.",None),("second idea.",None)],17.5)
    assert scenes[0].start==0 and scenes[-1].end==17.5
    assert abs(sum(s.end-s.start for s in scenes)-17.5)<0.01
def test_empty_script_has_no_scenes():
    assert split_script("  ")==[]
