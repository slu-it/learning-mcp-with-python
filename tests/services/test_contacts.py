import logging

from app.services.contacts import get_phone_number


async def test_known_contact_lowercase_returns_number():
    result = await get_phone_number("john")
    assert result == "555 123456"


async def test_known_contact_mixed_case_returns_number():
    result = await get_phone_number("JaNe")
    assert result == "555 654321"


async def test_known_contact_with_whitespace_returns_number():
    result = await get_phone_number("  john  ")
    assert result == "555 123456"


async def test_unknown_contact_returns_none():
    result = await get_phone_number("nobody")
    assert result is None


async def test_logger_is_called(caplog):
    with caplog.at_level(logging.INFO, logger="app.services.contacts"):
        await get_phone_number("john")

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.INFO
    assert "john" in record.message
    assert "555 123456" in record.message
