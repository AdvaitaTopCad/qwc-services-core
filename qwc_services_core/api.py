"""Utility code that enhances Flask-RESTX API."""
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple, Union

from flask import Request
from flask_restx import Api as BaseApi
from flask_restx.reqparse import Argument
from werkzeug.datastructures import MultiDict


class Api(BaseApi):
    """Custom Flask-RESTPlus Api subclass for overriding default root route.

    Note:
        The endpoint of route '/' must be named 'root'.

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

    def create_model(self, name: str, fields: List[Tuple[str, type]]) -> Any:
        """Helper for creating api models with ordered fields.

        Args:
            name: Model name.
            fields: List of tuples containing ``['field name', <type>]``.

        Returns:
            The model object.
        """
        return create_model(self, name, fields)


def create_model(api: Api, name: str, fields: List[Tuple[str, Any]]) -> Any:
    """Helper for creating api models with ordered fields.

    Args:
        api: Flask-RESTX Api object
        name: Model name
        fields: List of tuples containing ['field name', <type>]

    Returns:
        The model object.
    """
    d = OrderedDict()
    for field in fields:
        d[field[0]] = field[1]
    return api.model(name, d)


class CaseInsensitiveMultiDict(MultiDict):
    """A MultiDict subclass.

    This is used with RequestParser which is case-insensitive for query
    parameter key names.

    Example:
        >>> from qwc_services_core.api import CaseInsensitiveMultiDict
        >>> parser = CaseInsensitiveMultiDict({ 'key': 'value' })
        >>> 'key' in parser  # True
        >>> 'KEY' in parser  # True

    Attributes:
        lower_key_map
            A mapping from lowercase keys to the real keys.
    """

    lower_key_map: Dict[str, str]

    def __init__(self, mapping: Optional[Union[MultiDict, Dict[str, str]]] = None):
        """Constructor.

        Args:
            mapping: A mapping of keys to values.
        """
        super().__init__(mapping)
        self.lower_key_map = {key.lower(): key for key in self}

    def __contains__(self, key: Any) -> bool:
        """Check if key is in the dict.

        Args:
            key: The key to check.

        Returns:
            True if the key is in the dict.
        """
        return key.lower() in self.lower_key_map

    def getlist(self, key: Any) -> List[Any]:  # type: ignore
        """Get a list of values for a key.

        Args:
            key: The key to get values for.

        Returns:
            A list of values for the key.
        """
        return super().getlist(self.lower_key_map.get(key.lower()))

    def pop(self, key: Any):  # type: ignore
        """Remove a key and return its value.

        Note:
            The ``key in self`` will still return ``True`` because the key is
            not removed from internal map.

        Args:
            key: The key to remove.

        Returns:
            The value of the removed key.
        """
        return super().pop(self.lower_key_map.get(key.lower()))


class CaseInsensitiveArgument(Argument):
    """An argument that is case-insensitive for query parameter key names."""

    def source(self, request: Request) -> CaseInsensitiveMultiDict:
        """Create a case-insensitive multi-dictionary.

        Args:
            request: The flask request object to parse arguments from.
        """
        return CaseInsensitiveMultiDict(super().source(request))
