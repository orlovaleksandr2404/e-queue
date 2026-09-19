import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.core.database import get_db
from src.core.security import get_current_user, require_admin
from src.models.user import User
from src.models.window import Window
from src.models.service import Service
from src.models.ticket import Ticket, TicketStatus
from src.schemas.window import WindowCreate, WindowRead
from src.schemas.ticket import TicketRead

router = APIRouter(prefix="/windows", tags=["Windows & Operators"])

QUEUE_SERVICE_URL = os.getenv("QUEUE_SERVICE_URL", "http://backend-queue:8001")

@router.get("", response_model=list[WindowRead])
async def list_windows(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Window))
    return result.scalars().all()

@router.get("/{window_id}", response_model=WindowRead)
async def get_window(window_id: int, db: AsyncSession = Depends(get_db)):
    window = await db.get(Window, window_id)
    if not window:
        raise HTTPException(status_code=404, detail="Окно не найдено")
    return window

@router.post("", response_model=WindowRead, status_code=status.HTTP_201_CREATED)
async def create_window(
    data: WindowCreate, 
    db: AsyncSession = Depends(get_db), 
    admin=Depends(require_admin)
):
    existing = await db.execute(select(Window).where(Window.number == data.number))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Окно с таким номером уже существует")

    window = Window(number=data.number, name=data.name)
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

    chosen_ticket = None

    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            resp = await client.post(
                f"{QUEUE_SERVICE_URL}/api/v1/algorithm/next-ticket",
                json={
                    "window_id": window.id,
                    "window_number": window.number,
                    "service_ids": service_ids
                }
            )
            if resp.status_code == 200:
                ticket_id = resp.json().get("ticket_id")
                if ticket_id:
                    chosen_ticket = await db.get(Ticket, ticket_id)
    except Exception:
        chosen_ticket = None

    if not chosen_ticket:
        query = (
            select(Ticket)
            .where(Ticket.status == TicketStatus.WAITING, Ticket.service_id.in_(service_ids))
            .order_by(Ticket.priority.desc(), Ticket.created_at.asc())
            .limit(1)
        )
        result = await db.execute(query)
        chosen_ticket = result.scalar_one_or_none()

    if not chosen_ticket:
        raise HTTPException(status_code=404, detail="В очереди нет клиентов для данного окна")

    query_waiting = (
        select(Ticket)
        .where(Ticket.status == TicketStatus.WAITING, Ticket.service_id.in_(service_ids))
        .order_by(Ticket.created_at.asc())
    )
    waiting_tickets = (await db.execute(query_waiting)).scalars().all()
    if not waiting_tickets:
        raise HTTPException(status_code=404, detail="В очереди нет клиентов для данного окна")

    chosen_ticket = None

    try:
        candidates_payload = [
            {
                "id": t.id,
                "priority": t.priority,
                "created_at": t.created_at.isoformat(),
                "service_id": t.service_id
            }
            for t in waiting_tickets
        ]

        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.post(
                f"{QUEUE_SERVICE_URL}/api/v1/algorithm/next-ticket",
                json={
                    "window_id": window.id,
                    "window_service_ids": service_ids,
                    "candidates": candidates_payload
                }
            )
            if resp.status_code == 200:
                ticket_id = resp.json().get("ticket_id")
                if ticket_id:
                    chosen_ticket = await db.get(Ticket, ticket_id)
    except Exception:
        chosen_ticket = None

    if not chosen_ticket:
        query_fallback = (
            select(Ticket)
            .where(Ticket.status == TicketStatus.WAITING, Ticket.service_id.in_(service_ids))
            .order_by(Ticket.priority.desc(), Ticket.created_at.asc())
            .limit(1)
        )
        chosen_ticket = (await db.execute(query_fallback)).scalar_one_or_none()

    if not chosen_ticket:
        raise HTTPException(status_code=404, detail="Ошибка подбора талона")

    chosen_ticket.status = TicketStatus.CALLED
    chosen_ticket.window_id = window.id
    chosen_ticket.operator_id = user.id

    await db.commit()
    await db.refresh(chosen_ticket)
    return chosen_ticket

@router.post("/tickets/{ticket_id}/start", response_model=TicketRead)
async def start_ticket_service(
    ticket_id: int, 
    db: AsyncSession = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Талон не найден")
    if ticket.status != TicketStatus.CALLED:
        raise HTTPException(status_code=400, detail="Начать прием можно только для вызванного талона")

    ticket.status = TicketStatus.IN_SERVICE
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

@router.post("/tickets/{ticket_id}/missed", response_model=TicketRead)
async def mark_ticket_missed(
    ticket_id: int, 
    db: AsyncSession = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    ticket = await db.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Талон не найден")
    if ticket.status != TicketStatus.CALLED:
        raise HTTPException(status_code=400, detail="Отметить неявку можно только для вызванного талона")

    ticket.status = TicketStatus.MISSED
    await db.commit()
    await db.refresh(ticket)
    return ticket
