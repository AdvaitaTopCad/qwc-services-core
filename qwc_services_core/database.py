import os
from typing import Dict, Optional

from attrs import define, field
from sqlalchemy import Engine, create_engine

DEFAULT_GEODB_SRV = "qwc_geodb"
DEFAULT_GEODB_URL = "postgresql:///?service=%s" % DEFAULT_GEODB_SRV
DEFAULT_CONFIGDB_SRV = "qwc_configdb"
DEFAULT_CONFIGDB_URL = "postgresql:///?service=%s" % DEFAULT_CONFIGDB_SRV


@define
class DatabaseEngine:
    """Helper for database connections using SQLAlchemy engines.

    Attributes:
        engines: Dict of SQLAlchemy engines.
    """

    engines: Dict[str, Engine] = field(factory=dict, init=False)

    def db_engine(self, conn_str: str) -> Engine:
        """Get the database engine for the given connection string.

        Args:
            conn_str: DB connection string for SQLAlchemy engine.

        Returns:
            The SQLAlchemy engine.

        see http://docs.sqlalchemy.org/en/latest/core/engines.html#postgresql
        """
        engine = self.engines.get(conn_str)
        if not engine:
            engine = create_engine(conn_str, pool_pre_ping=True, echo=False)
            self.engines[conn_str] = engine
        return engine

    def db_engine_env(self, env_name: str, default: Optional[str] = None) -> Engine:
        """Return engine configured in environment variable.

        Args:
            env_name: The name of the environment variable.
            default: Default value if environment variable is not set.

        Returns:
            The SQLAlchemy engine.
        """
        conn_str = os.environ.get(env_name, default)
        if conn_str is None:
            raise Exception("db_engine_env: Environment variable %s not set" % env_name)
        return self.db_engine(conn_str)

    def geo_db(self) -> Engine:
        """Return engine for default GeoDB."""
        return self.db_engine_env("GEODB_URL", DEFAULT_GEODB_URL)

    def config_db(self) -> Engine:
        """Return engine for default ConfigDB."""
        return self.db_engine_env("CONFIGDB_URL", DEFAULT_CONFIGDB_URL)
