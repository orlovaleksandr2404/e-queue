from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.core.database import get_db
from src.core.security import require_admin
from src.models.user import User, UserRole
from src.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/operators", response_model=list[UserRead])
async def list_operators(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    result = await db.execute(select(User).where(User.role == UserRole.OPERATOR))
    return result.scalars().all()
