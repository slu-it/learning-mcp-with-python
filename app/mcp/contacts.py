from typing import Annotated

from pydantic import Field

from app.mcp import mcp
from app.services.contacts import get_phone_number


@mcp.tool()
async def get_phone_number_of_contact(
    name: Annotated[str, Field(description="Contact name to look up")],
) -> str:
    """Look up the phone number for a contact by name. Returns a not-found message if the contact has no number."""
    number = await get_phone_number(name)
    if not number:
        return f'No phone number found for "{name}"'
    return number
