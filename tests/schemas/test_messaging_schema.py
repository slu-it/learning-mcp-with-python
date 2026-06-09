import pytest
from pydantic import ValidationError

from app.schemas.messaging import Channel, SendMessageRequest


def make(**kwargs) -> SendMessageRequest:
    defaults = {
        "channel": Channel.WHATSAPP,
        "phone_number": "+49 123 456789",
        "message": "Hello",
    }
    return SendMessageRequest.model_validate({**defaults, **kwargs})


class TestChannel:
    def test_whatsapp_is_valid(self):
        assert Channel("WHATSAPP") is Channel.WHATSAPP

    def test_sms_is_valid(self):
        assert Channel("SMS") is Channel.SMS

    def test_unknown_value_raises(self):
        with pytest.raises(ValueError):
            Channel("TELEGRAM")


class TestPhoneNumber:
    def test_single_character_is_valid(self):
        req = make(phone_number="x")
        assert req.phone_number == "x"

    def test_empty_string_is_invalid(self):
        with pytest.raises(ValidationError):
            make(phone_number="")

    def test_accepts_camel_case_alias(self):
        req = SendMessageRequest.model_validate(
            {"channel": "WHATSAPP", "phoneNumber": "+49 123 456789", "message": "Hello"}
        )
        assert req.phone_number == "+49 123 456789"

    def test_accepts_snake_case_field_name(self):
        req = SendMessageRequest.model_validate(
            {
                "channel": "WHATSAPP",
                "phone_number": "+49 123 456789",
                "message": "Hello",
            }
        )
        assert req.phone_number == "+49 123 456789"


class TestMessage:
    def test_single_character_is_valid(self):
        req = make(message="x")
        assert req.message == "x"

    def test_empty_string_is_invalid(self):
        with pytest.raises(ValidationError):
            make(message="")

    def test_4096_characters_is_valid(self):
        req = make(message="x" * 4096)
        assert len(req.message) == 4096

    def test_4097_characters_is_invalid(self):
        with pytest.raises(ValidationError):
            make(message="x" * 4097)
