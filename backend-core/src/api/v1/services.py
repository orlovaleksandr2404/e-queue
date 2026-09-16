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

@router.post("", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
async def create_service(data: ServiceCreate, db: AsyncSession = Depends(get_db)):
    service = Service(**data.model_dump())
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service
