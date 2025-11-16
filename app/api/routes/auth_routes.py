from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.UserSchema import UserCreate, UserLogin
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])




# Signup Route
@router.post("/signup")
async def signup(
    data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    return await AuthService.signup(data, db)


# Login Route
@router.post("/Login")
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    return await AuthService.login(data, db)



# Refresh Token Route 
async def refresh_token(
        token_data: RefreshTokenSchema,
        db: AsyncSession = Depends(get_db)
):
    return await AuthService.refresh_token(token_data)
