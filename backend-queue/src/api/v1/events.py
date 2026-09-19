from fastapi import APIRouter, Header, HTTPException

from src.core.config import settings
from src.core.ws import manager
from src.schemas.events import BroadcastEvent, BroadcastResult

router = APIRouter(prefix="/events", tags=["events"])


def _check_key(x_api_key: str | None) -> None:
    if settings.EVENT_API_KEY and x_api_key != settings.EVENT_API_KEY:
        raise HTTPException(401, "Неверный API-ключ события")


@router.post("/broadcast", response_model=BroadcastResult)
async def broadcast(
    event: BroadcastEvent,
    x_api_key: str | None = Header(default=None, alias="X-Api-Key"),
):
    _check_key(x_api_key)
    delivered = await manager.broadcast(
        {"type": event.type, "payload": event.payload}
    )
    return BroadcastResult(ok=True, delivered=delivered)