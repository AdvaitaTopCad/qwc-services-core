"""Translation support."""
import glob
import json
import os
from typing import Any, Dict, Union, cast

from flask import Flask, Request


class Translator:
    """Class for translating strings via json files."""

    translations: Dict[str, Union[str, Dict[str, str]]]

    def __init__(self, app: Flask, request: Request):
        """Constructor.

        Args:
            app: Flask app
            request: Flask request
        """
        supported_locales = list(
            map(
                lambda path: os.path.basename(path)[0:-5],
                glob.glob("translations/*.json"),
            )
        )

        DEFAULT_LOCALE = os.environ.get("DEFAULT_LOCALE", "en")
        locale = (
            request.accept_languages.best_match(supported_locales) or DEFAULT_LOCALE
        )

        self.translations = {}
        try:
            path = os.path.join(app.root_path, "translations/%s.json" % locale)
            with open(path, "r") as f:
                self.translations = json.load(f)
        except Exception as e:
            app.logger.error(
                "Failed to load translation strings for locale '%s' "
                "from %s, loading default locale\n%s" % (locale, path, e)
            )
            path = os.path.join(app.root_path, "translations/%s.json" % DEFAULT_LOCALE)
            with open(path, "r") as f:
                self.translations = json.load(f)

    def tr(self, msg_id: str):
        """Translate a string.

        Args:
            msg_id: The message id as a path, with components
            separated by ``.``.

        Returns:
            The translated string if the key indicated by the path in `msg_id`
            was located or ``msg_id`` otherwise.
        """
        parts = msg_id.split(".")
        lookup = self.translations
        for part in parts:
            if isinstance(lookup, dict):
                # get next lookup level
                lookup = cast(Any, lookup.get(part))
            else:
                # lookup level too deep
                lookup = None
            if lookup is None:
                # return input msg_id if not found
                lookup = msg_id
                break

        return lookup
