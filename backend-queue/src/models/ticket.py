import enum
from datetime import date, datetime

from sqlalchemy import (
    Column, Date, DateTime, Enum, Integer, String
)
from src.core.database import Base


class TicketStatus(str, enum.Enum):
    waiting = "waiting"
    called = "called"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)

    # нумерация
    number = Column(String(10), nullable=False, index=True)
    seq = Column(Integer, nullable=False)
    queue_date = Column(Date, default=date.today, index=True)

    # денормализованные данные услуги (snapshot на момент выдачи)
    service_id = Column(Integer, nullable=False, index=True)
    service_name = Column(String(120), nullable=False, default="")
    service_prefix = Column(String(2), nullable=False, default="A")
    avg_minutes = Column(Integer, default=5)

    # денормализованные данные окна (заполняется при вызове)
    window_id = Column(Integer, nullable=True, index=True)
    window_number = Column(Integer, nullable=True)

    status = Column(Enum(TicketStatus), default=TicketStatus.waiting, index=True)
    priority = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    called_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    # опционально: id клиента, если в core есть клиентская база
    client_id = Column(Integer, nullable=True)

    # оценка качества обслуживания
    rating = Column(Integer, nullable=True)
    feedback_comment = Column(String(500), default="")