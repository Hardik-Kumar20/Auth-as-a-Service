from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# creating access token 
def create_access_token(data: Dict[str, Any], expires_delta: Optional[int] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)


        to_encode.update({"exp":expire})

        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
    


# Creating refreshing token 
def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[int] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + timedelta(days = expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(days = settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp" : expire})

    return jwt.encode(
        to_encode,
        settings.REFRESH_SECRET_KEY,
        algorithm=settings.ALGORITHM
    )    


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
            )
        return payload
    except JWTError:
        raise JWTError("Access token is invalid or expired")
    


def decode_refresh_token(token: str) -> dict:
    try:
        return jwt.decode(
            token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        raise JWTError("Refresh token is invalid or expired")
        