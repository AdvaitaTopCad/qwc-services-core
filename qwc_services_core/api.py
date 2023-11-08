from collections import OrderedDict
from typing import Any, Dict, Optional, Tuple, Union

from flask_restx import Api as BaseApi
from flask_restx.reqparse import Argument
from werkzeug.datastructures import MultiDict


class Api(BaseApi):
    """Custom Flask-RESTPlus Api subclass for overriding default root route

    NOTE: endpoint of route '/' must be named 'root'::

    >>> @api.route('/', endpoint='root')

    see also https://github.com/noirbizarre/flask-restplus/issues/247
    """

    def _register_doc(self, app_or_blueprint):
        if self._add_specs and self._doc:
            # Register documentation before root if enabled
            app_or_blueprint.add_url_rule(self._doc, "doc", self.render_doc)
        # skip default root route
        # app_or_blueprint.add_url_rule(self.prefix or '/', 'root',
        #                               self.render_root)

    def create_model(self, name, fields):
        """Helper for creating api models with ordered fields

        :param str name: Model name
        :param list fields: List of tuples containing ['field name', <type>]
        """
        return create_model(self, name, fields)


def create_model(api: Api, name: str, fields: Tuple[str, Any]):
    """
    Helper for creating api models with ordered fields.

    :param api: Flask-RESTX Api object
    :param name: Model name
    :param fields: List of tuples containing ['field name', <type>]
    """
    d = OrderedDict()
    for field in fields:
        d[field[0]] = field[1]
    return api.model(name, d)


class CaseInsensitiveMultiDict(MultiDict):
    """
    A MultiDict subclass to use with RequestParser which is
    case-insensitive for query parameter key names.

    Example
    -------

    >>> from qwc_services_core.api import CaseInsensitiveMultiDict
    >>> parser = CaseInsensitiveMultiDict({ 'key': 'value' })
    >>> 'key' in parser  # True
    >>> 'KEY' in parser  # True

    Attributes
    ----------

    lower_key_map : dict
        A mapping from lowercase keys to the real keys.
    """

    lower_key_map: Dict[str, str]

    def __init__(
            self,
            mapping: Optional[Union[MultiDict, Dict[str, str]]] = None
    ):
        super().__init__(mapping)
        self.lower_key_map = {key.lower(): key for key in self}

    def __contains__(self, key):
        return key.lower() in self.lower_key_map

    def getlist(self, key):
        return super().getlist(self.lower_key_map.get(key.lower()))

    def pop(self, key):
        return super().pop(self.lower_key_map.get(key.lower()))


class CaseInsensitiveArgument(Argument):
    def source(self, request):
        return CaseInsensitiveMultiDict(super().source(request))
