"""Tenant handler module."""
import os
import re
from datetime import datetime
from logging import Logger
from typing import Any, Dict, Optional, TypedDict

from attrs import define, field
from flask import request
from flask.sessions import SecureCookieSessionInterface

from .permissions_reader import PermissionsReader
from .runtime_config import RuntimeConfig

DEFAULT_TENANT = "default"


@define
class TenantHandlerBase:
    """Tenant handler base class.

    Attributes:
        tenant_name: The name of the tenant; the value is taken from the
            ``QWC_TENANT`` environment variable.
        tenant_header: The header name to use when extracting the tenant name
            from request headers (used as it is) or from WSGI middleware
            (prefixed by ``HTTP_``, upper-cased); the value is taken from the
            ``TENANT_HEADER`` environment variable.
        tenant_url_re: The RegEx pattern to use for extracting the name of
            the tenant from an URL; this value is ONLY used if the ``tenant_header``
            attribute is not set; the value is taken from the ``TENANT_URL_RE``
            environment variable.
    """

    tenant_name: Optional[str] = field(
        factory=lambda: os.environ.get("QWC_TENANT"), init=False
    )
    tenant_header: Optional[str] = field(
        factory=lambda: os.environ.get("TENANT_HEADER"), init=False
    )
    tenant_url_re: Optional[re.Pattern] = field(
        factory=lambda: re.compile(os.environ.get("TENANT_URL_RE", ""))
        if os.environ.get("TENANT_URL_RE")
        else None,
        init=False,
    )

    def is_multi(self) -> bool:
        """Return True if multi-tenancy is enabled.

        Any of the following environment variables enable multi-tenancy:
        - QWC_TENANT
        - TENANT_HEADER
        - TENANT_URL_RE
        """
        return bool(self.tenant_name or self.tenant_header or self.tenant_url_re)

    def tenant(self) -> str:
        """Return the name of the tenant for current request.

        The function looks for the tenant name in the request in the following order:
        - ``tenant_name`` attribute of this instance,
        - HTTP_``tenant_header`` header,
        - ``tenant_url_re`` pattern in URL.

        Returns:
            The name of the tenant or ``DEFAULT_TENANT`` if no tenant name
            could be found.
        """
        return self.request_tenant()

    def environ_tenant(self, environ: Dict[str, str]) -> str:
        """The name of the tenant for environ from WSGI middleware.

        Args:
            environ: WSGI environment variables

        Returns:
            The name of the tenant or ``DEFAULT_TENANT`` if no tenant name
            could be found.
        """
        return self.request_tenant(environ)

    def request_tenant(self, environ: Optional[Dict[str, str]] = None) -> str:
        """The name of the tenant for current request or environ.

        Args:
            environ: WSGI environment variables or ``None`` to use current request.

        Returns:
            The name of the tenant or ``DEFAULT_TENANT`` if no tenant name
            could be found.
        """
        if self.tenant_name:
            return self.tenant_name
        if self.tenant_header:
            if environ:
                return environ.get(
                    "HTTP_%s" % self.tenant_header.upper(), DEFAULT_TENANT
                )
            else:
                return request.headers.get(self.tenant_header, DEFAULT_TENANT)
        if self.tenant_url_re:
            if environ:
                # reconstruct request URL from environ
                # cf. https://peps.python.org/pep-3333/#url-reconstruction
                base_url = "%s://%s%s%s" % (
                    environ.get("wsgi.url_scheme", ""),
                    environ.get("HTTP_HOST", ""),
                    environ.get("SCRIPT_NAME", ""),
                    environ.get("PATH_INFO", ""),
                )
            else:
                base_url = request.base_url
            match = self.tenant_url_re.match(base_url)
            if match:
                return match.group(1)
            else:
                return DEFAULT_TENANT
        return DEFAULT_TENANT


class HandlerRecord(TypedDict):
    """Handler cache record.

    Attributes:
        handler: Service handler instance
        last_update: Timestamp of last config file update.
    """

    handler: Any
    last_update: datetime


@define
class TenantHandler(TenantHandlerBase):
    """Tenant handler with configuration cache.

    Attributes:
        logger: Logger instance
        handler_cache: Cache for service handlers; first level maps the
            name of the service handler to the list of tenants; second level
            maps the tenant name to the handler instance and the timestamp of
            the last config update.
    """

    logger: Logger
    handler_cache: Dict[str, Dict[str, HandlerRecord]] = field(factory=dict, init=False)

    def handler(self, service_name: str, handler_name: str, tenant: str):
        """Get service handler for tenant.

        Args:
            service_name: Service name used to determine the path of the
                configuration file.
            handler_name: Handler name (primary key into our cache).
            tenant: Tenant ID

        Returns:
            ``None`` if not yet registered or if config files have changed.
        """
        handlers = self.handler_cache.get(handler_name)
        if handlers:
            handler = handlers.get(tenant)
            if handler:
                # check for config updates
                last_update = self.last_config_update(service_name, tenant)
                if last_update and last_update < handler["last_update"]:
                    # cache is up-to-date
                    return handler["handler"]
                else:
                    # config has changed, remove handler from cache
                    if tenant in handlers:
                        del handlers[tenant]
                        self.logger.debug(
                            "Removed expired %s handler for %s tenant from cache",
                            handler_name,
                            tenant,
                        )
            else:
                self.logger.debug("No handler for %s tenant", tenant)
        else:
            self.logger.debug("No handler cache for %s handler", handler_name)
        return None

    def register_handler(self, handler_name: str, tenant: str, handler: Any) -> Any:
        """Register service handler for tenant.

        Args:
            handler_name: Handler name (primary key into our cache).
            tenant: Tenant ID.
            handler: Service handler instance.

        Returns:
            Service handler instance (``handler`` argument).
        """
        handlers = self.handler_cache.get(handler_name)
        if handlers is None:
            handlers = {}
            self.handler_cache[handler_name] = handlers
        handlers[tenant] = {"handler": handler, "last_update": datetime.utcnow()}
        return handler

    def last_config_update(self, service_name: str, tenant: str) -> Optional[datetime]:
        """Compute latest timestamp of config and permission files for a tenant.

        Args:
            service_name: Service name.
            tenant: Tenant ID.

        Returns:
            Latest timestamp of config and permission files or ``None`` if
            neither of these files exist.
        """
        last_config_update = None
        paths = [
            RuntimeConfig.config_file_path(service_name, tenant),
            PermissionsReader.permissions_file_path(tenant),
        ]
        for path in paths:
            if os.path.isfile(path):
                timestamp = datetime.utcfromtimestamp(os.path.getmtime(path))
                if last_config_update is None or timestamp > last_config_update:
                    last_config_update = timestamp

        return last_config_update


class TenantPrefixMiddleware:
    """WSGI middleware injecting tenant header in path"""

    def __init__(self, app, _header=None, _ignore_default=None):
        self.app = app
        self.tenant_handler = TenantHandlerBase()
        self.service_prefix = (
            os.environ.get("QWC_SERVICE_PREFIX", "/").rstrip("/") + "/"
        )

    def __call__(self, environ, start_response):
        # environ in request http://localhost:9090/base/pages/test.html?arg=1
        # /base is mountpoint (e.g. via WSGIScriptAlias)
        # 'REQUEST_URI': '/base/pages/test.html?arg=1'
        # 'SCRIPT_NAME': '/base'
        # 'PATH_INFO': '/pages/test.html'
        # 'QUERY_STRING': 'arg=1'
        # see also https://www.python.org/dev/peps/pep-3333/#environ-variables
        tenant = self.tenant_handler.environ_tenant(environ)

        if tenant and (
            self.tenant_handler.tenant_name or self.tenant_handler.tenant_header
        ):
            # add tenant path prefix for multitenancy
            # NOTE: skipped if tenant already in path when using TENANT_URL_RE
            prefix = self.service_prefix + tenant
            environ["SCRIPT_NAME"] = prefix + environ.get("SCRIPT_NAME", "")
        return self.app(environ, start_response)


class TenantSessionInterface(SecureCookieSessionInterface, TenantHandlerBase):
    """Flask session handler injecting tenant in JWT cookie path"""

    def __init__(self, environ):
        SecureCookieSessionInterface.__init__(self)
        TenantHandlerBase.__init__(self)
        self.service_prefix = environ.get("QWC_SERVICE_PREFIX", "").rstrip("/") + "/"

    def tenant_path_prefix(self):
        """Tenant path prefix /map/org1 ("$QWC_SERVICE_PREFIX/$TENANT")"""
        if self.is_multi():
            return self.service_prefix + self.tenant()
        else:
            return self.service_prefix

    def get_cookie_path(self, app):
        # https://flask.palletsprojects.com/en/1.1.x/api/#flask.sessions.SessionInterface.get_cookie_path
        prefix = self.tenant_path_prefix()
        # Set config as a side effect
        app.config["JWT_ACCESS_COOKIE_PATH"] = prefix
        return prefix
