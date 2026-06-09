from unittest.mock import AsyncMock, patch

import pytest

from app.mcp import mcp


@pytest.fixture
def mock_send_whatsapp():
    with patch("app.mcp.messaging.send_whatsapp", new_callable=AsyncMock) as mock:
        yield mock


class TestSendWhatsappMessageTool:
    async def test_returns_success_message(self, mock_send_whatsapp):
        content, _ = await mcp.call_tool(
            "send_whatsapp_message",
            {"phone_number": "+49 123 456789", "message": "Hello"},
        )
        assert content[0].text == "Message was sent."

    async def test_service_called_with_correct_args(self, mock_send_whatsapp):
        await mcp.call_tool(
            "send_whatsapp_message",
            {"phone_number": "+49 123 456789", "message": "Hello"},
        )
        mock_send_whatsapp.assert_awaited_once_with("+49 123 456789", "Hello")

    async def test_service_error_returns_failure_message(self, mock_send_whatsapp):
        mock_send_whatsapp.side_effect = Exception("Provider unavailable")
        content, _ = await mcp.call_tool(
            "send_whatsapp_message",
            {"phone_number": "+49 123 456789", "message": "Hello"},
        )
        assert content[0].text == "Failed to send message: Provider unavailable"
