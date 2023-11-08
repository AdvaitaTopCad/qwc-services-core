import pytest
from flask import Flask

from qwc_services_core.app import app_nocache


@pytest.fixture()
def app():
    app = Flask(__name__)
    app.config.update(
        {
            "TESTING": True,
        }
    )

    app_nocache(app)
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_app_nocache(client):
    response = client.get("/posts")
    assert response.headers["Cache-Control"] == "public, max-age=0"
    assert response.headers["Pragma"] == "no-cache"
    assert response.headers["Expires"] == "0"
