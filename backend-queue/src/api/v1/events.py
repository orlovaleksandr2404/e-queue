import logging
import secrets

from fastapi import APIRouter, Header, HTTPException, status

from src.core.config import settings
from src.core.ws import manager
from src.schemas.events import BroadcastEvent, BroadcastResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["events"])


def _validate_api_key(x_api_key: str | None) -> None:
    """
    Валидация X-Api-Key.

    Если EVENT_API_KEY не задан в окружении — считаем это dev-режимом
    и пропускаем запрос, но пишем предупреждение в лог.
    """
    expected = settings.EVENT_API_KEY
    if not expected:
        logger.warning(
            "EVENT_API_KEY не задан — /events/broadcast открыт без авторизации"
        )
        return

    if not x_api_key or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или отсутствующий API-ключ",
        )


@router.post("/broadcast", response_model=BroadcastResult)
async def broadcast(
    event: BroadcastEvent,
    x_api_key: str | None = Header(default=None, alias="X-Api-Key"),
) -> BroadcastResult:
    """
    Core присылает событие — queue рассылает его всем подключённым к /ws/queue.

    Ничего не хранится: если клиентов нет, событие просто уходит в никуда.
    Это осознанное поведение stateless-сервиса.
    """
    _validate_api_key(x_api_key)

    message = {"type": event.type, "payload": event.payload}
    delivered = await manager.broadcast(message)

    logger.info(
        "broadcast: type=%s delivered=%d", event.type, delivered
    )
    return BroadcastResult(ok=True, delivered=delivered)