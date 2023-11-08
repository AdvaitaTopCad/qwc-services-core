from unittest.mock import MagicMock

from qwc_services_core.database import DatabaseEngine


class TestDatabaseEngine:
    def test_db_engine(self, mocker):
        create_engine = mocker.patch("qwc_services_core.database.create_engine")
        engine = MagicMock()
        create_engine.return_value = engine
        de = DatabaseEngine()
        assert de.db_engine("sqlite:///:memory:") is engine
        assert de.db_engine("sqlite:///:memory:") is engine

    def test_db_engine_env(self, mocker):
        de = DatabaseEngine()
        de.engines = {"a": "b"}
        assert de.db_engine_env("GEODB_URL", "a") == "b"

    def test_geo_db(self):
        de = DatabaseEngine()
        de.engines = {"postgresql:///?service=qwc_geodb": "b"}
        assert de.geo_db() == "b"

    def test_config_db(self):
        de = DatabaseEngine()
        de.engines = {"postgresql:///?service=qwc_configdb": "b"}
        assert de.config_db() == "b"
