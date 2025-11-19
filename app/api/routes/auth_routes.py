from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.UserSchema import UserCreate, UserLogin
from app.services.auth_service import AuthService
from app.api.deps.auth import get_current_user
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
@router.post("/refresh")
async def refresh_token(
        token_data: RefreshTokenSchema,
        db: AsyncSession = Depends(get_db),
):
    return await AuthService.refresh_token(token_data)



@router.get("/me", repsonse_model = UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
