from pydantic import BaseModel, ConfigDict
from src.schemas.service import ServiceRead

class WindowCreate(BaseModel):
    number: int
    name: str
    service_ids: list[int] = []

class WindowRead(BaseModel):
    id: int
    number: int
    name: str
    is_active: bool
    services: list[ServiceRead] = []

    model_config = ConfigDict(from_attributes=True)
