import re
from unittest.mock import MagicMock

import pytest

from qwc_services_core.tenant_handler import TenantHandlerBase


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

    def test_tenant(self, mocker):
        testee = MagicMock()
        testee.request_tenant = MagicMock(return_value="foo")
        assert TenantHandlerBase.tenant(testee) == "foo"
        testee.request_tenant.assert_called_once_with()

    def test_environ_tenant(self, mocker):
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
