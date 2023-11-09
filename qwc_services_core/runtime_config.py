"""Runtime configuration helpers."""
import os
import re
from logging import Logger
from typing import Any, Dict, Optional, cast

from attrs import define, field
from flask import json
from werkzeug.utils import safe_join


@define
class RuntimeConfig:
    """Runtime configuration helper class.

    Attributes:
        service: The name of the service.
        logger: Logger instance
        config: Runtime config
    """

    service: str
    logger: Logger
    config: Dict[str, Any] = field(factory=dict, init=False)

    @staticmethod
    def config_file_path(service: str, tenant: str) -> Optional[str]:
        """Compute the path to the permissions JSON file for a tenant.

        Args:
            service: The name of the service.
            tenant: The ID of the tenant.

        Returns:
            The path to the JSON file containing the permissions.
        """
        config_path = os.environ.get("CONFIG_PATH", "config")
        filename = "%sConfig.json" % service
        return safe_join(config_path, tenant, filename)

    def read_config(self, tenant) -> "RuntimeConfig":
        """Read service config for a tenant from associated JSON file.

        Args:
            tenant: The ID of the tenant.

        Returns:
            self
        """
        runtime_config_path = cast(
            str, RuntimeConfig.config_file_path(self.service, tenant)
        )
        self.logger.info("Reading runtime config '%s'" % runtime_config_path)
        try:
            with open(runtime_config_path, encoding="utf-8") as fh:
                data = fh.read()
                # Replace env variables
                self.config = json.loads(ENVVAR_PATTERN.sub(env_repl, data))
        except Exception as e:
            self.logger.error(
                "Could not load runtime config '%s':\n%s" % (runtime_config_path, e)
            )
            self.config = {}
        return self

    def tenant_config(self, tenant):
        """Read service config for a tenant from associated JSON file.

        Args:
            tenant: The ID of the tenant.

        Returns:
            self
        """
        return self.read_config(tenant)

    def get(self, name: str, default: Any = None) -> Any:
        """Get config value.

        Args:
            name: Name of config value.
            default: Default value if not found.

        Returns:
            Config value.
        """
        val = self.config.get("config", {}).get(name, default)
        # Optional override from env var
        env_val = os.environ.get(name.upper())
        if env_val is not None:
            # Convert from string
            try:
                if val is None:
                    # unknown type --> no conversion
                    val = env_val
                elif type(val) in (list, dict):
                    val = json.loads(env_val)
                elif type(val) is bool:
                    # convert string to boolean
                    # cf. deprecated distutils.util.strtobool
                    #   https://docs.python.org/3.9/distutils/apiref.html#distutils.util.strtobool
                    if env_val.lower() in ("true", "t", "1", "on", "yes", "y"):
                        val = True
                    elif env_val.lower() in ("false", "f", "0", "off", "no", "n", ""):
                        # NOTE: also convert empty string to False
                        #       to support legacy env configs
                        #       (bool("") => False)
                        val = False
                    else:
                        raise Exception("Unknown boolean value for '%s'" % env_val)
                else:
                    val = type(val)(env_val)
            except Exception as e:
                self.logger.warning(
                    "Could not convert config override "
                    "from env '%s=%s' to %s:\n%s"
                    % (name.upper(), env_val, type(val), e)
                )

        return val

    def resources(self) -> Dict[str, Any]:
        """Get resources config."""
        return cast(Dict[str, Any], self.config.get("resources"))

    def resource(self, name) -> Dict[str, Any]:
        """Get a resource configuration for a resource name."""
        return self.config.get("resources", {}).get(name)


ENVVAR_PATTERN = re.compile(r"\$\$(\w+)\$\$")


def env_repl(match: re.Match) -> str:
    """Return the value of the environment variable indicated by the match."""
    name = match.group(1)
    val = os.environ.get(name, "")
    return val
