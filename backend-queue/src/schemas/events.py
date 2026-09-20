from typing import Any

from pydantic import BaseModel, Field, field_validator


class BroadcastEvent(BaseModel):
    type: str = Field(min_length=1, max_length=64)
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("type")
    @classmethod
    def _no_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("type не может быть пустым или пробельным")
        return v


class BroadcastResult(BaseModel):
    ok: bool
    delivered: int