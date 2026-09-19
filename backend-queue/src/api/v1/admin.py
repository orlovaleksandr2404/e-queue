from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.security import require_admin
from src.models.ticket import Ticket, TicketStatus
from src.schemas.stats import StatsOut

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=StatsOut)
def stats(
    day: date = Query(default_factory=date.today),
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    q = db.query(Ticket).filter(Ticket.queue_date == day)
    total = q.count()
    completed = q.filter(Ticket.status == TicketStatus.completed).count()
    cancelled = q.filter(Ticket.status == TicketStatus.cancelled).count()
    no_show = q.filter(Ticket.status == TicketStatus.no_show).count()
    waiting = q.filter(Ticket.status == TicketStatus.waiting).count()

    durations = (
        db.query(Ticket.started_at, Ticket.finished_at)
        .filter(
            Ticket.queue_date == day,
            Ticket.status == TicketStatus.completed,
            Ticket.started_at.isnot(None),
            Ticket.finished_at.isnot(None),
        )
        .all()
    )
    avg_service = (
        sum((f - s).total_seconds() for s, f in durations) / len(durations) / 60
        if durations else 0.0
    )

    waits = (
        db.query(Ticket.created_at, Ticket.called_at)
        .filter(Ticket.queue_date == day, Ticket.called_at.isnot(None))
        .all()
    )
    avg_wait = (
        sum((c - cr).total_seconds() for cr, c in waits) / len(waits) / 60
        if waits else 0.0
    )

    avg_rating = (
        db.query(func.avg(Ticket.rating))
        .filter(Ticket.queue_date == day, Ticket.rating.isnot(None))
        .scalar()
    )

    return StatsOut(
        date=day.isoformat(),
        total_tickets=total,
        completed=completed,
        cancelled=cancelled,
        no_show=no_show,
        waiting_now=waiting,
        avg_service_minutes=round(avg_service, 2),
        avg_wait_minutes=round(avg_wait, 2),
        avg_rating=round(avg_rating, 2) if avg_rating else None,
    )