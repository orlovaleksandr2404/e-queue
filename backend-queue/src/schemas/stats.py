from typing import Optional

from pydantic import BaseModel


class StatsOut(BaseModel):
    date: str
    total_tickets: int
    completed: int
    cancelled: int
    no_show: int
    waiting_now: int
    avg_service_minutes: float
    avg_wait_minutes: float
    avg_rating: Optional[float] = None