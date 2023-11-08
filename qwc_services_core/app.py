from flask import Flask, Request


def app_nocache(app: Flask):
    """Adds various cache-disabling headers to all responses returned by the
        application
    :param app: A flask application
    """

    @app.after_request
    def add_header(r: Request):
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers["Cache-Control"] = "public, max-age=0"
        return r
