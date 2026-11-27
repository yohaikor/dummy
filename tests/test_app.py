from app import app


def test_health():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_index():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    body = response.get_json()
    assert body["service"] == "dummy"
    assert body["message"] == "hello"
