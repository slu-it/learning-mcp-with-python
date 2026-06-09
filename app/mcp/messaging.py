from typing import Annotated

from pydantic import Field

from app.mcp import mcp
from app.services.messaging import send_whatsapp


@mcp.tool()
async def send_whatsapp_message(
    phone_number: Annotated[str, Field(description="Recipient's phone number.")],
    message: Annotated[str, Field(description="Message to send")],
) -> str:
    """Sends a message to a WhatsApp contact by phone number."""
    try:
        await send_whatsapp(phone_number, message)
    except Exception as e:
        return f"Failed to send message: {e}"
    return "Message was sent."
