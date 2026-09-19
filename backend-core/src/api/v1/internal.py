from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.core.database import get_db
from src.models.ticket import Ticket, TicketStatus
from src.models.service import Service
from src.models.window import Window, window_services

router = APIRouter(prefix="/internal", tags=["Internal Service Communication"])

@router.get("/tickets/waiting")
async def get_internal_waiting(service_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    query = (
        select(Ticket)
        .where(Ticket.status == TicketStatus.WAITING, Ticket.service_id == service_id)
        .order_by(Ticket.priority.desc(), Ticket.created_at.asc())
    )
    res = await db.execute(query)
    tickets = res.scalars().all()
    return [
        {
            "id": t.id,
            "priority": t.priority,
            "created_at": t.created_at.isoformat(),
            "service_id": t.service_id
        }
        for t in tickets
    ]

@router.get("/tickets/{ticket_id}")
async def get_internal_ticket(ticket_id: int, db: AsyncSession = Depends(get_db)):
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Талон не найден")
    
    service = await db.get(Service, ticket.service_id)
    return {
        "id": ticket.id,
        "number": ticket.number,
        "status": ticket.status.value,
        "priority": ticket.priority,
        "service_id": ticket.service_id,
        "created_at": ticket.created_at.isoformat(),
        "service": {
            "name": service.name if service else "",
            "avg_duration_minutes": service.avg_duration_minutes if service else 10
        } if service else None
    }

@router.get("/windows/active")
async def count_active_windows(service_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    query = (
        select(func.count(Window.id))
        .join(window_services, Window.id == window_services.c.window_id)
        .where(window_services.c.service_id == service_id)
    )
    res = await db.execute(query)
    count = res.scalar() or 1
    return {"count": max(count, 1)}
