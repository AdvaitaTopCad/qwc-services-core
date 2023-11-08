from unittest.mock import MagicMock

from flask_jwt_extended import JWTManager

from qwc_services_core.jwt import jwt_manager


class TestJwtManager:
    def test_call(self):
        app = MagicMock()
        app.config = {}
        api = MagicMock()
        jwt = jwt_manager(app, api)
        assert isinstance(jwt, JWTManager)
        assert app.config["JWT_TOKEN_LOCATION"] == ["headers", "cookies"]
        assert app.config["JWT_ACCESS_COOKIE_NAME"] == "access_token_cookie"
        assert app.config["JWT_COOKIE_CSRF_PROTECT"] == False
        assert app.config["JWT_CSRF_CHECK_FORM"] == True
        assert isinstance(app.config["JWT_SECRET_KEY"], bytes)
        assert app.config["JWT_ACCESS_COOKIE_PATH"] == "/"

        assert app.after_request.call_count == 1
        assert api.errorhandler.call_count == 1
