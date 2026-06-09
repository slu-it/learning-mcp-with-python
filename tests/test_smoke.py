from fastapi.testclient import TestClient

from app.main import app


def test_application_starts_and_serves_requests():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
