from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.messaging import router
from app.schemas.messaging import Channel
from app.services.messaging import MessagingError

ENDPOINT = "/api/messaging/send"
VALID_BODY = {
    "channel": "WHATSAPP",
    "phoneNumber": "+49 123 456789",
    "message": "Hello",
}


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def mock_send_message():
    with patch("app.services.messaging.send_message", new_callable=AsyncMock) as mock:
        yield mock


class TestSendMessageRouter:
    def test_valid_whatsapp_request_returns_204(self, client, mock_send_message):
        response = client.post(ENDPOINT, json=VALID_BODY)
        assert response.status_code == 204

    def test_valid_sms_request_returns_204(self, client, mock_send_message):
        body = {**VALID_BODY, "channel": "SMS"}
        response = client.post(ENDPOINT, json=body)
        assert response.status_code == 204

    def test_service_called_with_correct_args(self, client, mock_send_message):
        client.post(ENDPOINT, json=VALID_BODY)
        mock_send_message.assert_awaited_once_with(
            channel=Channel.WHATSAPP,
            phone_number="+49 123 456789",
            message="Hello",
        )

    def test_messaging_error_maps_to_502(self, client, mock_send_message):
        mock_send_message.side_effect = MessagingError("Provider unavailable")
        response = client.post(ENDPOINT, json=VALID_BODY)
        assert response.status_code == 502
        assert response.json()["detail"] == "Provider unavailable"

    def test_missing_phone_number_returns_422(self, client):
        body = {"channel": "WHATSAPP", "message": "Hello"}
        response = client.post(ENDPOINT, json=body)
        assert response.status_code == 422

    def test_unknown_channel_returns_422(self, client):
        body = {**VALID_BODY, "channel": "TELEGRAM"}
        response = client.post(ENDPOINT, json=body)
        assert response.status_code == 422

    def test_empty_message_returns_422(self, client):
        body = {**VALID_BODY, "message": ""}
        response = client.post(ENDPOINT, json=body)
        assert response.status_code == 422
