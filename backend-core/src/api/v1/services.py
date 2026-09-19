from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.core.database import get_db
from src.models.service import Service
from src.schemas.service import ServiceCreate, ServiceRead

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
async def create_service(data: ServiceCreate, db: AsyncSession = Depends(get_db)):
    service = Service(
        name=data.name,
        prefix=data.prefix.upper(),
        avg_duration_minutes=data.avg_duration_minutes
    )
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service
