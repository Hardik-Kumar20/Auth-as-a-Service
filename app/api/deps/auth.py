from fastapi import Depends, HttpException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asycio import AsyncSession
from sqlalchemy.future import select

from db import get_db
from db.models.user import User
from app.core.security import decode_access_token


#This tells FastAPI where clients will get tokens from(login endpoint)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
):
    """
    1. Take JWT from Autorization header
    2. Decode and verify it 
    3. Load user from DB
    4. Return the user object
    """

    # 1. Decode & validate token 
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HttpException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Could not valideate credentials"
        )


    # 2.  Get user id from token payload
    user_id = payload.get("sub")
    if user_id is None:
        raise HttpException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            details = "Invalid token paylaod",
        )
    
    # 3. Load the user from DB
    result = await db.execute(seelct(User).where(user.id == user_id))
    user = result.scalar_one_or_none()

    #4. check user exists & is active 
    if not user or not user.is_active:
        raise HttpException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Inactive or missing user",
        )
    
    return user







# Creating require_role(RBAC/admin check)

def require_role(required_role: str):
    """
    Factory that returns a dependency which:
    - Calls get_current_user
    _ Checks if the user has the required role 
    """

    async def _require_role(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HttpException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Insufficient Permission",
            )
        return current_user
    return _require_role