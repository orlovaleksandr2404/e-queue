from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        return jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
        )


def require_operator(payload: dict = Depends(get_token_payload)) -> dict:
    if payload.get("role") not in ("operator", "admin"):
        raise HTTPException(403, "Требуются права оператора")
    return payload


def require_admin(payload: dict = Depends(get_token_payload)) -> dict:
    if payload.get("role") != "admin":
        raise HTTPException(403, "Требуются права администратора")
    return payload