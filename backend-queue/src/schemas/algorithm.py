from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Candidate(BaseModel):
    id: int
    priority: int = 0
    created_at: datetime
    service_id: int


class NextTicketRequest(BaseModel):
    window_id: int
    window_service_ids: list[int] = []
    candidates: list[Candidate]


class NextTicketResponse(BaseModel):
    ticket_id: Optional[int] = None
    reason: str = "none_available"


class WaitTimeResponse(BaseModel):
    ticket_id: int
    number: str
    service_name: str
    position: int
    eta_minutes: int


class EtaRequest(BaseModel):
    position: int = Field(ge=1)
    avg_minutes: int = Field(ge=1)
    active_windows: int = Field(default=1, ge=1)


class EtaResponse(BaseModel):
    eta_minutes: int