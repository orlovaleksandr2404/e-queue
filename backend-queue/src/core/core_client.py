import time
from typing import Any, Optional

import httpx
from fastapi import HTTPException

from src.core.config import settings


class _TTLCache:
    def __init__(self, ttl: int) -> None:
        self.ttl = ttl
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        expires_at, value = item
        if expires_at < time.time():
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.time() + self.ttl, value)


_cache = _TTLCache(settings.CORE_CACHE_TTL)
_client = httpx.Client(base_url=settings.CORE_API_URL, timeout=settings.CORE_TIMEOUT)


def _get(path: str, cache_key: str) -> dict:
    cached = _cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        r = _client.get(path)
    except httpx.HTTPError as e:
        raise HTTPException(502, f"backend-core недоступен: {e}")

    if r.status_code == 404:
        raise HTTPException(404, "Объект не найден в backend-core")
    if r.status_code >= 400:
        raise HTTPException(502, f"backend-core вернул {r.status_code}")

    data = r.json()
    _cache.set(cache_key, data)
    return data


def get_service(service_id: int) -> dict:
    return _get(f"/api/v1/services/{service_id}", f"service:{service_id}")


def get_window(window_id: int) -> dict:
    return _get(f"/api/v1/windows/{window_id}", f"window:{window_id}")


def invalidate_service(service_id: int) -> None:
    _cache._store.pop(f"service:{service_id}", None)


def invalidate_window(window_id: int) -> None:
    _cache._store.pop(f"window:{window_id}", None)