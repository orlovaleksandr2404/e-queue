from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class OrganizationBase(BaseModel):
    name: str
    address: Optional[str] = None
    is_active: bool = True

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationRead(OrganizationBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
