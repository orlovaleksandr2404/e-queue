from typing import Optional
from pydantic import BaseModel, ConfigDict
from src.models.user import UserRole

class UserRead(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    role: UserRole

    model_config = ConfigDict(from_attributes=True)
