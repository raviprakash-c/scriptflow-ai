from app.providers import search_footage
def test_candidate_has_rights_metadata():
    asset,score,reason=search_footage("weekly savings budget")
    assert asset.source and asset.license and asset.attribution
    assert 0<=score<=1 and reason
def test_different_clip_id_when_possible():
    a,_,_=search_footage("technology")
    b,_,_=search_footage("technology",used_ids={a.footage_id})
    assert a.footage_id!=b.footage_id
def test_mock_not_claimed_cleared():
    asset,_,_=search_footage("trees nature")
    assert asset.commercial_use is False
