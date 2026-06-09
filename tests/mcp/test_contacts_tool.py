from unittest.mock import AsyncMock, patch

import pytest

from app.mcp import mcp


@pytest.fixture
def mock_get_phone_number():
    with patch("app.mcp.contacts.get_phone_number", new_callable=AsyncMock) as mock:
        yield mock


class TestGetPhoneNumberOfContactTool:
    async def test_returns_phone_number_when_found(self, mock_get_phone_number):
        mock_get_phone_number.return_value = "+49 123 456789"
        content, _ = await mcp.call_tool(
            "get_phone_number_of_contact", {"name": "Alice"}
        )
        assert content[0].text == "+49 123 456789"

    async def test_service_called_with_correct_args(self, mock_get_phone_number):
        mock_get_phone_number.return_value = "+49 123 456789"
        await mcp.call_tool("get_phone_number_of_contact", {"name": "Alice"})
        mock_get_phone_number.assert_awaited_once_with("Alice")

    async def test_returns_not_found_message_when_contact_has_no_number(
        self, mock_get_phone_number
    ):
        mock_get_phone_number.return_value = None
        content, _ = await mcp.call_tool(
            "get_phone_number_of_contact", {"name": "Unknown"}
        )
        assert content[0].text == 'No phone number found for "Unknown"'
