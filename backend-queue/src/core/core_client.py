import httpx
from fastapi import HTTPException

from src.core.config import settings

_client = httpx.AsyncClient(
    base_url=settings.CORE_API_URL,
    timeout=settings.CORE_TIMEOUT,
)


async def _get(path: str, params: dict | None = None):
    try:
        r = await _client.get(path, params=params)
    except httpx.HTTPError as e:
        raise HTTPException(502, f"backend-core недоступен: {e}")

    if r.status_code == 404:
        raise HTTPException(404, "Объект не найден в backend-core")
    if r.status_code >= 400:
        raise HTTPException(502, f"backend-core вернул {r.status_code}")
    return r.json()


async def fetch_ticket(ticket_id: int) -> dict:
    return await _get(f"/api/v1/internal/tickets/{ticket_id}")


async def fetch_waiting(service_id: int) -> list[dict]:
    return await _get("/api/v1/internal/tickets/waiting", {"service_id": service_id})


async def count_active_windows(service_id: int) -> int:
    data = await _get("/api/v1/internal/windows/active", {"service_id": service_id})
    return int(data.get("count") or settings.DEFAULT_ACTIVE_WINDOWS)