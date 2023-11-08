def test_app_nocache(client):
    response = client.get("/posts")
    assert response.headers["Cache-Control"] == "public, max-age=0"
    assert response.headers["Pragma"] == "no-cache"
    assert response.headers["Expires"] == "0"
