from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.core_client import get_service
from src.core.database import get_db
from src.core.ws import manager
from src.models.ticket import Ticket, TicketStatus
from src.schemas.ticket import (
    FeedbackIn, TicketCreate, TicketOut, TicketStatusOut,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


def queue_snapshot(db: Session) -> dict:
    today = date.today()
    waiting = (
        db.query(Ticket)
        .filter(Ticket.status == TicketStatus.waiting, Ticket.queue_date == today)
        .order_by(Ticket.priority.desc(), Ticket.created_at.asc())
        .all()
    )
    called = (
        db.query(Ticket)
        .filter(
            Ticket.status.in_([TicketStatus.called, TicketStatus.in_progress]),
            Ticket.queue_date == today,
        )
        .all()
    )
    return {
        "waiting": [
            {"id": t.id, "number": t.number, "service": t.service_name}
            for t in waiting
        ],
        "called": [
            {
                "id": t.id,
                "number": t.number,
                "window": t.window_number,
                "status": t.status.value,
            }
            for t in called
        ],
    }


@router.post("", response_model=TicketOut, status_code=201)
async def take_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    service = get_service(payload.service_id)

    if service.get("is_active") is False:
        raise HTTPException(400, "Услуга неактивна")

    today = date.today()

    last = (
        db.query(Ticket)
        .filter(Ticket.service_id == service["id"], Ticket.queue_date == today)
        .order_by(Ticket.seq.desc())
        .first()
    )
    seq = (last.seq + 1) if last else 1

    ticket = Ticket(
        number=f"{service['prefix']}-{seq:03d}",
        seq=seq,
        queue_date=today,
        service_id=service["id"],
        service_name=service["name"],
        service_prefix=service["prefix"],
        avg_minutes=service.get("avg_duration_minutes", 10),
        priority=payload.priority,
        client_id=payload.client_id,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    await manager.broadcast({"type": "queue_update", "data": queue_snapshot(db)})
    return ticket

@router.get("/{ticket_id}", response_model=TicketStatusOut)
def ticket_status(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Талон не найден")

    if ticket.status == TicketStatus.waiting:
        ahead = (
            db.query(Ticket)
            .filter(
                Ticket.status == TicketStatus.waiting,
                Ticket.queue_date == ticket.queue_date,
                Ticket.service_id == ticket.service_id,
                Ticket.created_at < ticket.created_at,
            )
            .count()
        )
        return TicketStatusOut(
            number=ticket.number,
            status=ticket.status.value,
            service_name=ticket.service_name,
            position=ahead + 1,
            eta_minutes=ahead * ticket.avg_minutes,
        )

    return TicketStatusOut(
        number=ticket.number,
        status=ticket.status.value,
        service_name=ticket.service_name,
    )


@router.post("/{ticket_id}/cancel", response_model=TicketOut)
async def cancel_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Талон не найден")
    if ticket.status not in (TicketStatus.waiting, TicketStatus.called):
        raise HTTPException(400, "Нельзя отменить талон в текущем статусе")
    ticket.status = TicketStatus.cancelled
    db.commit()
    db.refresh(ticket)
    await manager.broadcast(
        {"type": "queue_update", "data": queue_snapshot(db)}
    )
    return ticket


@router.post("/{ticket_id}/feedback", response_model=TicketOut)
async def leave_feedback(
    ticket_id: int, data: FeedbackIn, db: Session = Depends(get_db)
):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Талон не найден")
    if ticket.status != TicketStatus.completed:
        raise HTTPException(400, "Оценить можно только завершённый талон")
    if ticket.rating is not None:
        raise HTTPException(400, "Оценка уже оставлена")
    ticket.rating = data.rating
    ticket.feedback_comment = data.comment
    db.commit()
    db.refresh(ticket)
    return ticket