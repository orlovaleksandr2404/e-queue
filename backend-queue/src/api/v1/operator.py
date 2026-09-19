from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.v1.tickets import queue_snapshot
from src.core.core_client import get_window
from src.core.database import get_db
from src.core.security import require_operator
from src.core.ws import manager
from src.models.ticket import Ticket, TicketStatus
from src.schemas.ticket import TicketOut

router = APIRouter(prefix="/operator", tags=["operator"])


@router.post("/call-next", response_model=TicketOut)
async def call_next(
    window_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_operator),
):
    # окно валидируем в backend-core
    window = get_window(window_id)
    if not window.get("is_active", True):
        raise HTTPException(400, "Окно неактивно")

    ticket = (
        db.query(Ticket)
        .filter(Ticket.status == TicketStatus.waiting)
        .order_by(Ticket.priority.desc(), Ticket.created_at.asc())
        .first()
    )
    if not ticket:
        raise HTTPException(404, "Очередь пуста")

    ticket.status = TicketStatus.called
    ticket.window_id = window["id"]
    ticket.window_number = window["number"]
    ticket.called_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)

    await manager.broadcast(
        {
            "type": "ticket_called",
            "number": ticket.number,
            "window": ticket.window_number,
        }
    )
    await manager.broadcast(
        {"type": "queue_update", "data": queue_snapshot(db)}
    )
    return ticket


@router.post("/tickets/{ticket_id}/start", response_model=TicketOut)
async def start_service(
    ticket_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_operator),
):
    ticket = db.get(Ticket, ticket_id)
    if not ticket or ticket.status != TicketStatus.called:
        raise HTTPException(400, "Талон не в статусе 'вызван'")
    ticket.status = TicketStatus.in_progress
    ticket.started_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    await manager.broadcast(
        {"type": "queue_update", "data": queue_snapshot(db)}
    )
    return ticket


@router.post("/tickets/{ticket_id}/finish", response_model=TicketOut)
async def finish(
    ticket_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_operator),
):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Талон не найден")
    ticket.status = TicketStatus.completed
    ticket.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    await manager.broadcast(
        {"type": "queue_update", "data": queue_snapshot(db)}
    )
    return ticket


@router.post("/tickets/{ticket_id}/no-show", response_model=TicketOut)
async def no_show(
    ticket_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_operator),
):
    ticket = db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(404, "Талон не найден")
    ticket.status = TicketStatus.no_show
    ticket.finished_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    await manager.broadcast(
        {"type": "queue_update", "data": queue_snapshot(db)}
    )
    return ticket


@router.get("/queue")
def current_queue(
    db: Session = Depends(get_db),
    _: dict = Depends(require_operator),
):
    return queue_snapshot(db)