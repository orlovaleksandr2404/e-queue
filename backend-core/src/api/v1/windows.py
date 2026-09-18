from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.core.database import get_db
from src.core.security import get_current_user
from src.models.user import User
from src.models.window import Window
from src.models.service import Service
from src.models.ticket import Ticket, TicketStatus
from src.schemas.window import WindowCreate, WindowRead
from src.schemas.ticket import TicketRead

router = APIRouter(prefix="/windows", tags=["Windows & Operators"])

@router.get("", response_model=list[WindowRead])
async def list_windows(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Window))
    return result.scalars().all()

@router.post("", response_model=WindowRead, status_code=status.HTTP_201_CREATED)
async def create_window(data: WindowCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    window = Window(name=data.name)
    if data.service_ids:
        services_res = await db.execute(select(Service).where(Service.id.in_(data.service_ids)))
        window.services = list(services_res.scalars().all())

    db.add(window)
    await db.commit()
    await db.refresh(window)
    return window

@router.post("/{window_id}/call-next", response_model=TicketRead)
async def call_next_ticket(
    window_id: int, 
    db: AsyncSession = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    window = await db.get(Window, window_id)
    if not window:
        raise HTTPException(status_code=404, detail="Окно не найдено")

    service_ids = [s.id for s in window.services]
    if not service_ids:
        raise HTTPException(status_code=400, detail="К данному окну не привязано ни одной услуги")

    query = (
        select(Ticket)
        .where(Ticket.status == TicketStatus.WAITING, Ticket.service_id.in_(service_ids))
        .order_by(Ticket.created_at.asc())
        .limit(1)
    )
    result = await db.execute(query)
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="В очереди нет клиентов для данного окна")

    ticket.status = TicketStatus.CALLED
    ticket.window_id = window.id
    ticket.operator_id = user.id

    await db.commit()
    await db.refresh(ticket)
    return ticket

@router.post("/tickets/{ticket_id}/complete", response_model=TicketRead)
async def complete_ticket(
    ticket_id: int, 
    db: AsyncSession = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Талон не найден")

    ticket.status = TicketStatus.COMPLETED
    await db.commit()
    await db.refresh(ticket)
    return ticket
