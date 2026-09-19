from typing import Any

from pydantic import BaseModel


class BroadcastEvent(BaseModel):
    type: str
    payload: dict[str, Any] = {}


class BroadcastResult(BaseModel):
    ok: bool
    delivered: int