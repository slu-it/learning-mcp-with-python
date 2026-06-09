from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class Channel(str, Enum):
    """Supported delivery channels.

    Both channels address the recipient by phone number. Add new
    members here and the API will validate incoming values against
    them automatically (an unknown channel yields a 422 response).
    """

    WHATSAPP = "WHATSAPP"
    SMS = "SMS"


class SendMessageRequest(BaseModel):
    """Request body for POST /api/messaging/send."""

    model_config = ConfigDict(
        # Accept the camelCase alias on input, and also allow the
        # snake_case field name (handy in tests and internal callers).
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "channel": "WHATSAPP",
                "phoneNumber": "+49 123 123456",
                "message": "Hello World!",
            }
        },
    )

    channel: Channel
    # The wire format uses camelCase ("phoneNumber"); the alias maps it
    # to a snake_case Python attribute. Kept as a plain string so values
    # like "+49 123 123456" (with spaces) are accepted. For strict
    # validation, see the pydantic-extra-types PhoneNumber type.
    phone_number: str = Field(alias="phoneNumber", min_length=1)
    message: str = Field(min_length=1, max_length=4096)
