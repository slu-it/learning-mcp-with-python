from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import require_api_scope
from app.schemas.messaging import SendMessageRequest
from app.services import messaging as messaging_service
from app.services.messaging import MessagingError

router = APIRouter(
    prefix="/api/messaging",
    tags=["messaging"],
    dependencies=[Depends(require_api_scope)],
)


@router.post(
    "/send",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Send a message through the given channel",
)
async def send_message(request: SendMessageRequest) -> None:
    """Accept a message and hand it off to the messaging service.

    Returns 204 No Content on success. Malformed bodies (missing fields,
    unknown channel, etc.) are rejected with 422 automatically by FastAPI
    before this function runs.
    """
    try:
        await messaging_service.send_message(
            channel=request.channel,
            phone_number=request.phone_number,
            message=request.message,
        )
    except MessagingError as exc:
        # Translate a downstream provider failure into a 502.
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    return None
