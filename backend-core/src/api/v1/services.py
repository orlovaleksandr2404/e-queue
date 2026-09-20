from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy import select
from src.core.database import get_db
from src.core.security import require_admin
from src.models.service import Service
from src.schemas.service import ServiceCreate, ServiceRead
from src.models.ticket import Ticket

router = APIRouter(prefix="/services", tags=["Services"])

@router.get("", response_model=list[ServiceRead])
async def list_services(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service))
    return result.scalars().all()

@router.get("/{service_id}", response_model=ServiceRead)
async def get_service(service_id: int, db: AsyncSession = Depends(get_db)):
    service = await db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")
    return service

@router.post("", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
async def create_service(data: ServiceCreate, db: AsyncSession = Depends(get_db), admin=Depends(require_admin)):
    service = Service(
        name=data.name,
        prefix=data.prefix.upper(),
        avg_duration_minutes=data.avg_duration_minutes
    )
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(require_admin)
):
    service = await db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Услуга не найдена")

    ticket_count_res = await db.execute(
        select(func.count(Ticket.id)).where(Ticket.service_id == service_id)
    )
    if (ticket_count_res.scalar() or 0) > 0:
        raise HTTPException(
            status_code=400,
            detail="Невозможно удалить услугу, по которой уже существуют талоны в очереди"
        )

    await db.delete(service)
    await db.commit()
    return None
