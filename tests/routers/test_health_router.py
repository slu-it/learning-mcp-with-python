import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.health import router

ENDPOINT = "/health"


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestHealthRouter:
    def test_returns_200(self, client):
        response = client.get(ENDPOINT)
        assert response.status_code == 200

    def test_returns_ok_status(self, client):
        response = client.get(ENDPOINT)
        assert response.json() == {"status": "ok"}
