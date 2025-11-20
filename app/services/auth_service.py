from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas.UserSchema import RefreshTokenSchema

from app.db.models.user import User
from app.core.security import(
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token
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
            hashed_password = hashed_pw,
            is_active = True
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        new_user.refresh_token_version += 1
        await db.commit()
        await db.refresh(new_user)

        access = create_access_token({"sub": new_user.id})
        refresh = create_refresh_token({"sub": new_user.id, "ver": new_user.refresh_token_version})

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
        
        user.refresh_token_version += 1
        await db.commit()
        await db.refresh(user)

        access = create_access_token({"sub": user.id})
        refresh = create_refresh_token({"sub": user.id})

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer"
        }


    @staticmethod
    async def refresh_token(token_data: RefreshTokenSchema, db: AsyncSession):
        try:
            payload = decode_refresh_token(token_data.refresh_token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        user_id = payload.get("sub")
        token_version = payload.get("ver")

        if user_id is None or token_version is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload",
            )

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Check if token version matches
        if user.refresh_token_version != token_version:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked",
            )

        # Rotate version
        user.refresh_token_version += 1
        await db.commit()
        await db.refresh(user)

        new_access = create_access_token({"sub": user.id})
        new_refresh = create_refresh_token(
            {"sub": user.id, "ver": user.refresh_token_version}
        )

        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
        }