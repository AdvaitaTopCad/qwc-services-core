import re
from unittest.mock import MagicMock

import pytest
from attr import define

from qwc_services_core.tenant_handler import (
    TenantHandler,
    TenantHandlerBase,
    TenantPrefixMiddleware,
    TenantSessionInterface,
)


@pytest.fixture
def h_base():
    return TenantHandlerBase()


class TestTenantHandlerBase:
    def test_init(self, mocker):
        # os = mocker.patch("qwc_services_core.tenant_handler.os")
        mocker.patch.dict(
            "os.environ",
            {
                "QWC_TENANT": "foo",
                "TENANT_HEADER": "bar",
                "TENANT_URL_RE": "baz",
            },
        )
        handler = TenantHandlerBase()
        assert handler.tenant_name == "foo"
        assert handler.tenant_header == "bar"
        assert handler.tenant_url_re.pattern == "baz"

    def test_is_multi(self, mocker):
        mocker.patch.dict(
            "os.environ",
            {
                "QWC_TENANT": "",
                "TENANT_HEADER": "",
                "TENANT_URL_RE": "",
            },
        )
        handler = TenantHandlerBase()
        assert not handler.is_multi()

    def test_is_multi_1(self, mocker):
        mocker.patch.dict(
            "os.environ",
            {
                "QWC_TENANT": "foo",
                "TENANT_HEADER": "",
                "TENANT_URL_RE": "",
            },
        )
        handler = TenantHandlerBase()
        assert handler.is_multi()

    def test_is_multi_2(self, mocker):
        mocker.patch.dict(
            "os.environ",
            {
                "QWC_TENANT": "",
                "TENANT_HEADER": "bar",
                "TENANT_URL_RE": "",
            },
        )
        handler = TenantHandlerBase()
        assert handler.is_multi()

    def test_is_multi_3(self, mocker):
        mocker.patch.dict(
            "os.environ",
            {
                "QWC_TENANT": "",
                "TENANT_HEADER": "",
                "TENANT_URL_RE": "baz",
            },
        )
        handler = TenantHandlerBase()
        assert handler.is_multi()

    def test_tenant(self):
        testee = MagicMock()
        testee.request_tenant = MagicMock(return_value="foo")
        assert TenantHandlerBase.tenant(testee) == "foo"
        testee.request_tenant.assert_called_once_with()

    def test_environ_tenant(self):
        testee = MagicMock()
        testee.request_tenant = MagicMock(return_value="foo")
        assert TenantHandlerBase.environ_tenant(testee, "bar") == "foo"
        testee.request_tenant.assert_called_once_with("bar")

    class TestRequestTenant:
        def test_using_name(self, h_base):
            h_base.tenant_name = "foo"
            assert h_base.request_tenant() == "foo"

        def test_using_header_and_environ(self, h_base):
            h_base.tenant_header = "bar"

            environ = {"HTTP_BAR": "foo"}
            assert h_base.request_tenant(environ) == "foo"

            environ = {"NO_HTTP_BAR": "foo"}
            assert h_base.request_tenant(environ) == "default"

        def test_using_header_and_request(self, h_base, app, mocker):
            h_base.tenant_header = "bar"
            with app.test_request_context("/"):
                request = mocker.patch("qwc_services_core.tenant_handler.request")
                request.headers = {"bar": "foo"}
                assert h_base.request_tenant() == "foo"

                request.headers = {}
                assert h_base.request_tenant() == "default"

        def test_using_url_re_and_environ(self, h_base):
            URL = "http://localhost/foo/bar"
            h_base.tenant_url_re = re.compile(f"^({URL})$")
            environ = {
                "wsgi.url_scheme": "http",
                "HTTP_HOST": "localhost",
                "SCRIPT_NAME": "/foo",
                "PATH_INFO": "/bar",
            }
            assert h_base.request_tenant(environ) == URL

            environ = {"PATH_INFO": "lorem"}
            assert h_base.request_tenant(environ) == "default"

        def test_using_url_re_and_request(self, h_base, app, mocker):
            URL = "http://localhost/foo/bar"
            h_base.tenant_url_re = re.compile(f"^({URL})$")
            with app.test_request_context("/"):
                request = mocker.patch("qwc_services_core.tenant_handler.request")
                request.base_url = URL
                assert h_base.request_tenant() == URL

                request.base_url = "lorem"
                assert h_base.request_tenant() == "default"

        def test_empty(self, h_base):
            assert h_base.request_tenant() == "default"


@pytest.fixture
def h_full():
    # https://www.attrs.org/en/stable/glossary.html#term-slotted-classes
    # We do this trick to be able to mock class methods.
    @define(slots=False)
    class TenantHandlerProxy(TenantHandler):
        pass

    return TenantHandlerProxy(logger=MagicMock())


class TestTenantHandler:
    class TestHandler:
        def test_no_handlers(self, h_full):
            h_full.handler_cache = {}
            assert h_full.handler("foo", "bar", "baz") is None

            h_full.handler_cache = {
                "x": {"y": {"z": "lorem"}},
            }
            assert h_full.handler("foo", "bar", "baz") is None

        def test_no_tenant(self, h_full):
            h_full.handler_cache = {
                "bar": {"y": {"z": "lorem"}},
            }
            assert h_full.handler("foo", "bar", "bazX") is None

        def test_no_update_time(self, h_full, mocker):
            mocker.patch.object(h_full, "last_config_update", return_value=None)
            h_full.handler_cache = {
                "bar": {"baz": {"z": "lorem"}},
            }
            assert h_full.handler("foo", "bar", "baz") is None
            assert h_full.handler_cache == {
                "bar": {},
            }

        def test_expired(self, h_full, mocker):
            mocker.patch.object(h_full, "last_config_update", return_value=1)
            h_full.handler_cache = {
                "bar": {"baz": {"last_update": 0, "handler": "lorem"}},
            }
            assert h_full.handler("foo", "bar", "baz") is None
            assert h_full.handler_cache == {
                "bar": {},
            }

        def test_found(self, h_full, mocker):
            mocker.patch.object(h_full, "last_config_update", return_value=1)
            h_full.handler_cache = {
                "bar": {"baz": {"last_update": 2, "handler": "lorem"}},
            }
            assert h_full.handler("foo", "bar", "baz") == "lorem"
            assert h_full.handler_cache == {
                "bar": {"baz": {"last_update": 2, "handler": "lorem"}},
            }

    class TestRegister:
        def test_register_handler(self, h_full, mocker):
            datetime = mocker.patch("qwc_services_core.tenant_handler.datetime")
            datetime.utcnow.return_value = 123
            h_full.handler_cache = {}
            assert h_full.register_handler("foo", "bar", "baz") == "baz"
            assert h_full.handler_cache == {
                "foo": {"bar": {"last_update": 123, "handler": "baz"}},
            }

        def test_update_existing(self, h_full, mocker):
            datetime = mocker.patch("qwc_services_core.tenant_handler.datetime")
            datetime.utcnow.return_value = 123
            h_full.handler_cache = {
                "foo": {"bar": {"last_update": 789, "handler": "xyz"}},
            }
            assert h_full.register_handler("foo", "bar", "baz") == "baz"
            assert h_full.handler_cache == {
                "foo": {"bar": {"last_update": 123, "handler": "baz"}},
            }

    class TestLastConfigUpdate:
        def test_no_files(self, h_full, tmp_path, mocker):
            rc = mocker.patch("qwc_services_core.tenant_handler.RuntimeConfig")
            rc.config_file_path.return_value = tmp_path / "foo"
            pr = mocker.patch("qwc_services_core.tenant_handler.PermissionsReader")
            pr.permissions_file_path.return_value = tmp_path / "bar"
            assert h_full.last_config_update("x", "y") is None

        def test_with_files(self, h_full, tmp_path, mocker):
            rc = mocker.patch("qwc_services_core.tenant_handler.RuntimeConfig")
            rc.config_file_path.return_value = tmp_path / "foo"
            pr = mocker.patch("qwc_services_core.tenant_handler.PermissionsReader")
            pr.permissions_file_path.return_value = tmp_path / "bar"
            datetime = mocker.patch("qwc_services_core.tenant_handler.datetime")
            datetime.utcfromtimestamp.return_value = 123

            (tmp_path / "foo").touch()
            assert h_full.last_config_update("x", "y") == 123
            assert datetime.utcfromtimestamp.call_count == 1
            assert rc.config_file_path.call_count == 1
            assert pr.permissions_file_path.call_count == 1

            (tmp_path / "bar").touch()
            assert h_full.last_config_update("x", "y") == 123


class TestTenantPrefixMiddleware:
    def test_init(self):
        app = MagicMock()
        testee = TenantPrefixMiddleware(app)
        assert testee.app is app
        assert isinstance(testee.tenant_handler, TenantHandlerBase)
        assert testee.service_prefix == "/"


class TestTenantSessionInterface:
    def test_init_no_env(self, mocker):
        environ = MagicMock()
        environ.get.return_value = ""
        testee = TenantSessionInterface(environ)
        assert testee.service_prefix == "/"

    def test_init_env(self, mocker):
        environ = MagicMock()
        environ.get.return_value = "foo"
        testee = TenantSessionInterface(environ)
        assert testee.service_prefix == "foo/"
