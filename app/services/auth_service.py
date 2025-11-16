from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.user import User
from app.core.security import(
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)

from app.schemas.UserSchema import UserCreate, UserLogin, UserOut


class AuthService:
    @staticmethod
    async def signup(data: UserCreate, db: AsyncSession):
        result = await db.execute(select(User).where(User.email == data.email))
        existing_user = result.scalar_one_or_none()


        if existing_user:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Email already registered"
            )
        
        hashed_pw = hash_password(data.password)

        new_user = User(
            email = data.email,
            password_hash = hashed_pw,
            is_active = True
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)


        access = create_access_token({"sub": new_user.id})
        refresh = create_refresh_token({"sub": new_user.id})

        return{
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer"
        }
    


@staticmethod
async def login(data: UserLogin, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User not found"
        )
    
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code = status.HTTP_404_BAD_REQUEST,
            detail = "Invalid password"
        )
    
    access = create_access_token({"sub": user.id})
    refresh = create_refresh_token({"sub": user.id})

    return {
        "access_token": access,
        "token_type": "bearer"
    }

@staticmethod
async def refresh_token(token_data: RefreshTokenSchema):
    payload = decode_token(token_data.refresh_token)
    user_id = payload.get("sub")

    new_access = create_access_token({"sub": user_id})
    new_refresh = create_refresh_token({"sub": user_id})

    return {
            "access_token": new_access,
            "refresh_token": new_refresh
        }