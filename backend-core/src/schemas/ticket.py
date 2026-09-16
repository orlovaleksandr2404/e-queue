from datetime import datetime
from pydantic import BaseModel, ConfigDict
from src.models.ticket import TicketStatus

class TicketCreate(BaseModel):
    service_id: int

class TicketRead(BaseModel):
    id: int
    number: str
    status: TicketStatus
    service_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
