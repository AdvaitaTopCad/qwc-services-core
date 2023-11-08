"""Enhancement of the Flask application object."""
from flask import Flask, Request


def app_nocache(app: Flask):
    """Adds cache-disabling headers to all responses returned by the application.

    Args:
        app: The flask application to change.
    """

    @app.after_request
    def add_header(r: Request):
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers["Cache-Control"] = "public, max-age=0"
        return r
