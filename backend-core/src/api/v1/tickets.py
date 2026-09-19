from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.core.database import get_db
from src.models.service import Service
from src.models.ticket import Ticket, TicketStatus
from src.schemas.ticket import TicketCreate, TicketRead

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.get("/board", response_model=list[TicketRead])
async def get_board_tickets(db: AsyncSession = Depends(get_db)):
    query = (
        select(Ticket)
        .where(Ticket.status == TicketStatus.CALLED)
        .order_by(Ticket.created_at.desc())
        .limit(10)
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.post("", response_model=TicketRead, status_code=status.HTTP_201_CREATED)
async def issue_ticket(data: TicketCreate, db: AsyncSession = Depends(get_db)):
    service = await db.get(Service, data.service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    count_query = select(func.count(Ticket.id)).where(Ticket.service_id == data.service_id)
    result = await db.execute(count_query)
    current_count = result.scalar() or 0
    ticket_number = f"{service.prefix}-{current_count + 1:02d}"

    ticket = Ticket(
        number=ticket_number,
        service_id=service.id,
        status=TicketStatus.WAITING,
        priority=data.priority
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket
