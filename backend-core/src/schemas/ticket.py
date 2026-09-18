from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from src.models.ticket import TicketStatus

class TicketCreate(BaseModel):
    service_id: int

class TicketRead(BaseModel):
    id: int
    number: str
    status: TicketStatus
    service_id: int
    window_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
