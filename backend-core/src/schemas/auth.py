from pydantic import BaseModel, ConfigDict
from src.models.user import UserRole

class UserRegister(BaseModel):
    username: str
    password: str
    full_name: str
    role: UserRole = UserRole.OPERATOR

class UserRead(BaseModel):
    id: int
    username: str
    full_name: str
    role: UserRole
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    role: UserRole
    user_id: int
