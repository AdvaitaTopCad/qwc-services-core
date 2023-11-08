from unittest.mock import MagicMock


class TestApi:
    def test_create_model(self, mocker):
        """Test create_model() helper function"""
        mocker.patch('qwc_services_core.api.create_model')
        from qwc_services_core.api import Api, create_model

        api = Api()
        fields = [
            ('field1', str),
            ('field2', int)
        ]

        api.create_model('test_model', fields)

        create_model.assert_called_with(
            api, 'test_model', fields
        )


def test_create_model():
    """Test create_model() helper function"""
    from qwc_services_core.api import create_model, Api
    api = MagicMock()
    fields = [
        ('field1', str),
        ('field2', int)
    ]
    create_model(api, "some_name", fields)
    api.model.assert_called_with("some_name", {
        "field1": str,
        "field2": int
    })


class TestCaseInsensitiveMultiDict:
    def test_init(self):
        """Test __init__() method"""
        from qwc_services_core.api import CaseInsensitiveMultiDict

        d = CaseInsensitiveMultiDict({
            'key1': 'value',
            'KEY2': 'value'
        })

        assert d.lower_key_map == {'key1': 'key1', 'key2': 'KEY2'}

    def test_contains(self):
        """Test __contains__() method"""
        from qwc_services_core.api import CaseInsensitiveMultiDict

        d = CaseInsensitiveMultiDict({
            'key': 'value'
        })

        assert 'key' in d
        assert 'KEY' in d

    def test_getlist(self):
        """Test getlist() method"""
        from qwc_services_core.api import CaseInsensitiveMultiDict

        d = CaseInsensitiveMultiDict({
            'key1': 'value',
            'KEY2': ['value2', 'other2']
        })

        assert d.getlist('key') == []
        assert d.getlist('key1') == ['value']
        assert d.getlist('KEY2') == ['value2', 'other2']
        assert d.getlist('Key2') == ['value2', 'other2']
        assert d.getlist('key2') == ['value2', 'other2']

    def test_pop(self):
        """Test pop() method"""
        from qwc_services_core.api import CaseInsensitiveMultiDict

        d = CaseInsensitiveMultiDict({
            'key1': 'value',
            'KEY2': ['value2', 'other2']
        })
        assert d.getlist('key1') == ['value']
        assert d.pop('key1') == 'value'
        assert d.getlist('key1') == []


class TestCaseInsensitiveArgument:
    def test_source(self):
        """Test source() method"""
        from qwc_services_core.api import (
            CaseInsensitiveMultiDict, 
            CaseInsensitiveArgument
        )

        arg = CaseInsensitiveArgument('test', 'test')
        request = MagicMock()
        request.get_json = MagicMock(return_value={'key1': 'json-value'})
        request.values = {
            'key1': 'value',
            'KEY2': ['value2', 'other2']
        }
        result = arg.source(request)
        assert isinstance(result, CaseInsensitiveMultiDict)
        assert result.getlist('key1') == ['json-value', 'value']
        assert result.getlist('KEY2') == ['value2', 'other2']
