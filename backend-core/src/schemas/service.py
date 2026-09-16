from pydantic import BaseModel, ConfigDict

class ServiceBase(BaseModel):
    name: str
    prefix: str
    avg_duration_minutes: int = 10

class ServiceCreate(ServiceBase):
    pass

class ServiceRead(ServiceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
