from unittest.mock import MagicMock

from qwc_services_core.translator import Translator


class TestTranslator:
    def test_init(self, mocker, tmp_path):
        json_file = tmp_path / "en.json"
        with open(json_file, "w") as f:
            f.write('{"lorem": "ipsum"}')
        glob = mocker.patch("qwc_services_core.translator.glob")
        os = mocker.patch("qwc_services_core.translator.os")

        glob.glob.return_value = ["translations/en.json"]
        os.path.join.return_value = json_file

        app = MagicMock()
        req = MagicMock()
        t = Translator(app, req)

        glob.glob.assert_called_with("translations/*.json")
        assert t.translations == {"lorem": "ipsum"}

    def test_tr(self, mocker, tmp_path):
        json_file = tmp_path / "en.json"
        with open(json_file, "w") as f:
            f.write('{"lorem": "ipsum"}')
        os = mocker.patch("qwc_services_core.translator.os")
        os.path.join.return_value = json_file

        app = MagicMock()
        req = MagicMock()
        t = Translator(app, req)
        t.translations = {"lorem": "ipsum"}
        assert t.tr("lorem") == "ipsum"
        assert t.tr("dolor") is "dolor"

        t.translations = {
            "lorem": {
                "ipsum": {
                    "dolor": "sit",
                },
            }
        }
        assert t.tr("lorem.ipsum.dolor") == "sit"
        assert t.tr("lorem.ipsum") == {"dolor": "sit"}
