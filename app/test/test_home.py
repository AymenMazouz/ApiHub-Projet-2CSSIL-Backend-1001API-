from flask.testing import FlaskClient


def test_home(client: FlaskClient):
    response = client.get("/")
    assert response.status_code == 200
    assert b"ITOUCH API MARKETPLACE API DOCUMENTATION" in response.data
