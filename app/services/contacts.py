import logging

_CONTACT_NUMBERS: dict[str, str] = {
    "john": "555 123456",
    "jane": "555 654321",
}

logger = logging.getLogger(__name__)


async def get_phone_number(name: str) -> str | None:
    """Look up the phone number for a contact by name. Returns None if the contact has no number."""
    number = _CONTACT_NUMBERS.get(name.strip().lower())
    logger.info('returning number for "%s": %s', name, number)
    return number
