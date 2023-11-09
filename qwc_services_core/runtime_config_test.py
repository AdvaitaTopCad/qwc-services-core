import re

from qwc_services_core.runtime_config import RuntimeConfig, env_repl


class TestRuntimeConfig:
    def test_config_file_path(self, mocker):
        os = mocker.patch("qwc_services_core.runtime_config.os")

        os.environ = {}
        assert (
            RuntimeConfig.config_file_path("foo", "bar") == "config/bar/fooConfig.json"
        )

        os.environ = {"CONFIG_PATH": "baz"}
        assert (
            RuntimeConfig.config_file_path("test", "test") == "baz/test/testConfig.json"
        )

    def test_read_config(self, mocker, tmp_path):
        os = mocker.patch("qwc_services_core.runtime_config.os")

        os.environ = {"CONFIG_PATH": str(tmp_path)}
        logger = mocker.MagicMock()
        testee = RuntimeConfig(service="foo", logger=logger)
        testee.config = {}
        assert testee == testee.read_config("bar")
        assert testee.config == {}

        (tmp_path / "bar").mkdir()
        (tmp_path / "bar" / "fooConfig.json").write_text('{"x": "y"}')
        assert testee == testee.read_config("bar")
        assert testee.config == {"x": "y"}

        (tmp_path / "bar" / "fooConfig.json").write_text('{"x": "$$lorem$$"}')
        assert testee == testee.read_config("bar")
        assert testee.config == {"x": ""}

        os.environ = {"CONFIG_PATH": str(tmp_path), "lorem": "ipsum"}
        (tmp_path / "bar" / "fooConfig.json").write_text('{"x": "$$lorem$$"}')
        assert testee == testee.read_config("bar")
        assert testee.config == {"x": "ipsum"}

    def test_tenant_config(self, mocker, tmp_path):
        os = mocker.patch("qwc_services_core.runtime_config.os")

        os.environ = {"CONFIG_PATH": str(tmp_path)}
        logger = mocker.MagicMock()
        testee = RuntimeConfig(service="foo", logger=logger)
        testee.config = {}
        assert testee == testee.tenant_config("bar")
        assert testee.config == {}

    def test_get(self, mocker):
        os = mocker.patch("qwc_services_core.runtime_config.os")
        os.environ = {}
        logger = mocker.MagicMock()
        testee = RuntimeConfig(service="foo", logger=logger)

        testee.config = {}
        assert testee.get("bar") is None

        testee.config = {"config": {}}
        assert testee.get("bar") is None

        testee.config = {"config": {"bar": "baz"}}
        assert testee.get("bar") == "baz"

        testee.config = {}
        assert testee.get("bar", "foo") == "foo"

        testee.config = {"config": {}}
        os.environ = {"BAR": "baz"}
        assert testee.get("bar") == "baz"
        assert testee.get("BAR") == "baz"

        testee.config = {
            "config": {
                "bar": "baz1",
                "lorem": 1,
                "IpSUM": [1, 2, 3],
                "dolor": {"bar": "baz2", "lorem": 2, "IpSUM": [4, 5, 6]},
                "a_float_var": 1.23,
            }
        }
        os.environ = {
            "BAR": "baz2",
            "LOREM": "2",
            "IPSUM": "[4, 5, 6]",
            "DOLOR": '{"sit": "amet"}',
            "A_FLOAT_VAR": "With a string value",
        }
        assert testee.get("bar") == "baz2"
        assert testee.get("lorem") == 2
        assert testee.get("IpSUM") == [4, 5, 6]
        assert testee.get("dolor") == {"sit": "amet"}
        assert testee.get("a_float_var") == 1.23

    def test_resources(self, mocker):
        os = mocker.patch("qwc_services_core.runtime_config.os")
        os.environ = {}
        logger = mocker.MagicMock()
        testee = RuntimeConfig(service="foo", logger=logger)

        testee.config = {}
        assert testee.resources() is None

        testee.config = {"resources": "foo"}
        assert testee.resources() == "foo"

    def test_resource(self, mocker):
        os = mocker.patch("qwc_services_core.runtime_config.os")
        os.environ = {}
        logger = mocker.MagicMock()
        testee = RuntimeConfig(service="foo", logger=logger)

        testee.config = {}
        assert testee.resource("bar") is None

        testee.config = {"resources": {}}
        assert testee.resource("bar") is None

        testee.config = {"resources": {"bar": "baz"}}
        assert testee.resource("bar") == "baz"


def test_env_repl(mocker):
    os = mocker.patch("qwc_services_core.runtime_config.os")
    match = re.match(r"\$\$(\w+)\$\$", "$$lorem$$")

    os.environ = {}
    assert env_repl(match) == ""

    os.environ = {"lorem": "ipsum"}
    assert env_repl(match) == "ipsum"
