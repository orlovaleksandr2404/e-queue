from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.core.database import get_db
from src.core.security import get_current_user
from src.models.user import User
from src.models.organization import Organization
from src.schemas.organization import OrganizationCreate, OrganizationRead

router = APIRouter(prefix="/organizations", tags=["Organizations"])

@router.get("", response_model=list[OrganizationRead])
async def list_organizations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Organization))
    return result.scalars().all()

@router.get("/{org_id}", response_model=OrganizationRead)
async def get_organization(org_id: int, db: AsyncSession = Depends(get_db)):
    org = await db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Организация не найдена")
    return org

@router.post("", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
async def create_organization(
    data: OrganizationCreate, 
    db: AsyncSession = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    existing = await db.execute(select(Organization).where(Organization.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Организация с таким названием уже существует")

    org = Organization(
        name=data.name,
        address=data.address,
        is_active=data.is_active
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org
