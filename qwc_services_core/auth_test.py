def test_get_username():
    from qwc_services_core.auth import get_username

    assert get_username(None) is None
    assert get_username("foo") == "foo"
    assert get_username({"username": "foo"}) == "foo"
    assert get_username({"xxx": "foo"}) == None
