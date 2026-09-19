from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TicketCreate(BaseModel):
    service_id: int
    priority: int = 0
    client_id: Optional[int] = None


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    number: str
    status: str
    service_id: int
    service_name: str
    window_id: Optional[int]
    window_number: Optional[int]
    priority: int
    created_at: datetime
    called_at: Optional[datetime]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    rating: Optional[int] = None


class TicketStatusOut(BaseModel):
    number: str
    status: str
    service_name: str
    position: Optional[int] = None
    eta_minutes: Optional[int] = None


class FeedbackIn(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str = ""


class QueueSnapshot(BaseModel):
    waiting: list[dict]
    called: list[dict]