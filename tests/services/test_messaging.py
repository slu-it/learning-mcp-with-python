import logging
from unittest.mock import AsyncMock, patch

from app.schemas.messaging import Channel
from app.services.messaging import send_message, send_sms, send_whatsapp


# ---------------------------------------------------------------------------
# send_message dispatch tests
# ---------------------------------------------------------------------------


async def test_send_message_whatsapp_dispatches_to_send_whatsapp():
    """send_message with Channel.WHATSAPP delegates to send_whatsapp."""
    with patch(
        "app.services.messaging.send_whatsapp", new_callable=AsyncMock
    ) as mock_whatsapp:
        await send_message(Channel.WHATSAPP, "+49 123 456789", "Hello WhatsApp")

    mock_whatsapp.assert_awaited_once_with("+49 123 456789", "Hello WhatsApp")


async def test_send_message_sms_dispatches_to_send_sms():
    """send_message with Channel.SMS delegates to send_sms."""
    with patch("app.services.messaging.send_sms", new_callable=AsyncMock) as mock_sms:
        await send_message(Channel.SMS, "+49 987 654321", "Hello SMS")

    mock_sms.assert_awaited_once_with("+49 987 654321", "Hello SMS")


# ---------------------------------------------------------------------------
# Logging tests for the low-level handlers
# ---------------------------------------------------------------------------


async def test_send_whatsapp_logs_correct_message(caplog):
    with caplog.at_level(logging.INFO, logger="app.services.messaging"):
        await send_whatsapp("+49 123 456789", "Hello WhatsApp")

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.INFO
    assert "+49 123 456789" in record.message
    assert "Hello WhatsApp" in record.message


async def test_send_sms_logs_correct_message(caplog):
    with caplog.at_level(logging.INFO, logger="app.services.messaging"):
        await send_sms("+49 987 654321", "Hello SMS")

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.INFO
    assert "+49 987 654321" in record.message
    assert "Hello SMS" in record.message
