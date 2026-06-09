import logging

from app.schemas.messaging import Channel

logger = logging.getLogger(__name__)


class MessagingError(Exception):
    """Raised when a message could not be delivered to the provider."""


async def send_message(channel: Channel, phone_number: str, message: str) -> None:
    """Dispatch a message to the appropriate channel handler."""
    if channel is Channel.WHATSAPP:
        await send_whatsapp(phone_number, message)
    elif channel is Channel.SMS:
        await send_sms(phone_number, message)
    else:
        # Unreachable while the enum and the branches stay in sync, but it
        # guards against a forgotten branch when you add a new channel.
        raise MessagingError(f"Unsupported channel: {channel}")


async def send_whatsapp(phone_number: str, message: str) -> None:
    logger.info("WhatsApp -> %s: %s", phone_number, message)


async def send_sms(phone_number: str, message: str) -> None:
    logger.info("SMS -> %s: %s", phone_number, message)
