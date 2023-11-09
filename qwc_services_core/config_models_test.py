from unittest.mock import MagicMock

from qwc_services_core.config_models import ConfigModels


class A:
    pass


class B:
    name = MagicMock()
    classes = MagicMock()
    prepare = MagicMock()


class TestConfigModels:
    def test_init_no_string(self, mocker):
        init_models = mocker.patch.object(ConfigModels, "init_models")
        db_engine = MagicMock()
        testee = ConfigModels(db_engine)
        assert db_engine.config_db.called
        assert db_engine.db_engine.not_called
        assert testee.base is None
        assert testee.custom_models == {}
        assert init_models.called

    def test_init_with_string(self, mocker):
        init_models = mocker.patch.object(ConfigModels, "init_models")
        db_engine = MagicMock()
        testee = ConfigModels(db_engine, "foo")
        assert db_engine.config_db.not_called
        assert db_engine.db_engine.called_with("foo")
        assert testee.base is None
        assert testee.custom_models == {}
        assert init_models.called

    def test_session(self, mocker):
        Session = mocker.patch("qwc_services_core.config_models.Session")
        mocker.patch.object(ConfigModels, "init_models")
        db_engine = MagicMock()
        testee = ConfigModels(db_engine)
        testee.engine = MagicMock()
        testee.session()
        assert Session.called_with(testee.engine)

    def test_model(self, mocker):
        mocker.patch.object(ConfigModels, "init_models")
        db_engine = MagicMock()
        testee = ConfigModels(db_engine)
        testee.base = MagicMock()
        testee.base.classes.get.return_value = None
        testee.user_model = MagicMock()
        testee.custom_models = {"foo": "bar"}
        assert testee.model("users") == testee.user_model
        assert testee.model("foo") == "bar"
        assert testee.model("baz") is None
        assert testee.base.classes.get.call_count == 2

    def test_init_models(self, mocker):
        mocker.patch("qwc_services_core.config_models.UserMixin", A)
        relationship = mocker.patch("qwc_services_core.config_models.relationship")

        mocker.patch("qwc_services_core.config_models.MetaData")
        automap_base = mocker.patch("qwc_services_core.config_models.automap_base")
        automap_base.return_value = B
        db_engine = MagicMock()
        testee = ConfigModels(db_engine, extra_tables=["foo", "bar"])

        assert B.prepare.call_count == 1
        assert relationship.call_count == 17
        assert testee.user_model.user_info
        assert testee.user_model.sorted_groups
        assert testee.user_model.sorted_roles
        assert testee.user_model.registration_requests
