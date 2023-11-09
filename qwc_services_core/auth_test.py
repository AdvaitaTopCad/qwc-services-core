from unittest.mock import MagicMock

import qwc_services_core.auth


def test_get_username():
    from qwc_services_core.auth import get_username

    assert get_username(None) is None
    assert get_username("foo") == "foo"
    assert get_username({"username": "foo"}) == "foo"
    assert get_username({"xxx": "foo"}) is None


def test_get_groups():
    from qwc_services_core.auth import get_groups

    assert get_groups(None) == []
    assert get_groups("foo") == []
    assert get_groups({"groups": ["foo", "bar"]}) == ["foo", "bar"]
    assert get_groups(
        {
            "groups": ["foo", "bar"],
            "group": "baz",
        }
    ) == ["foo", "bar", "baz"]
    assert get_groups({"xxx": "foo"}) == []


class TestGetAuthUser:
    def test_with_identity(self, mocker):
        mocker.patch("qwc_services_core.auth.get_jwt_identity")
        from qwc_services_core.auth import get_auth_user, get_jwt_identity

        get_jwt_identity.return_value = "foo"

        assert get_auth_user() == "foo"

    def test_without_identity_no_basic_auth(self, mocker):
        mocker.patch("qwc_services_core.auth.get_jwt_identity")
        mocker.patch.object(qwc_services_core.auth, "ALLOW_BASIC_AUTH_USER", False)
        from qwc_services_core.auth import get_auth_user, get_jwt_identity

        get_jwt_identity.return_value = None

        assert get_auth_user() is None

    def test_without_identity_and_basic_auth(self, app, mocker):
        with app.test_request_context("/"):
            mocker.patch("qwc_services_core.auth.get_jwt_identity")
            mocker.patch("qwc_services_core.auth.request")
            mocker.patch.object(qwc_services_core.auth, "ALLOW_BASIC_AUTH_USER", True)
            from qwc_services_core.auth import get_auth_user, get_jwt_identity, request

            get_jwt_identity.return_value = None
            request.authorization = None

            assert get_auth_user() is None

            request.authorization = MagicMock()
            request.authorization.username = "foo"
            assert get_auth_user() == "foo"


class TestGroupNameMapper:
    def test_init(self, mocker):
        os = mocker.patch("qwc_services_core.auth.os")
        from qwc_services_core.auth import GroupNameMapper

        os.environ = {}
        mapper = GroupNameMapper()
        assert mapper.group_mappings == []

        os.environ = {}
        mapper = GroupNameMapper("abc~efg")
        assert len(mapper.group_mappings) == 1
        assert mapper.group_mappings[0][0].pattern == "abc"
        assert mapper.group_mappings[0][1] == "efg"

        os.environ = {}
        mapper = GroupNameMapper("abc~efg#foo~bar")
        assert len(mapper.group_mappings) == 2
        assert mapper.group_mappings[0][0].pattern == "abc"
        assert mapper.group_mappings[0][1] == "efg"
        assert mapper.group_mappings[1][0].pattern == "foo"
        assert mapper.group_mappings[1][1] == "bar"

        os.environ = {}
        mapper = GroupNameMapper("abc~#foo")
        assert len(mapper.group_mappings) == 2
        assert mapper.group_mappings[0][0].pattern == "abc"
        assert mapper.group_mappings[0][1] == ""
        assert mapper.group_mappings[1][0].pattern == "foo"
        assert mapper.group_mappings[1][1] == ""

        os.environ = {"GROUP_MAPPINGS": "abc~efg#foo~bar#baz"}
        mapper = GroupNameMapper()
        assert len(mapper.group_mappings) == 3
        assert mapper.group_mappings[0][0].pattern == "abc"
        assert mapper.group_mappings[0][1] == "efg"
        assert mapper.group_mappings[1][0].pattern == "foo"
        assert mapper.group_mappings[1][1] == "bar"
        assert mapper.group_mappings[2][0].pattern == "baz"
        assert mapper.group_mappings[2][1] == ""

    def test_mapped_group(self, mocker):
        mocker.patch("qwc_services_core.auth.os")
        from qwc_services_core.auth import GroupNameMapper, os

        os.environ = {}

        mapper = GroupNameMapper()
        assert mapper.mapped_group("ship_crew") == "ship_crew"

        mapper = GroupNameMapper("ship_crew~crew")
        assert mapper.mapped_group("ship_crew") == "crew"

        mapper = GroupNameMapper("foo~lorem")
        assert mapper.mapped_group(["foo", "bar"]) == "lorem bar"
