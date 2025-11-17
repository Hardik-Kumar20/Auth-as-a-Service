import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import engine, async_session
from app.db.base import Base
from app.db.models.user import User
from app.core.security import hash_password



async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_initial_admin():
    async with async_session() as db:
        result = await db.execute(
            User._table_.select().where(User.emial == "admin@example.com")
        )
        existing = result.first()
        if existing:
            return
        
        admin = User(
            email = "admin@example.com",
            password_hash = hash_password("Admin@123"),
            is_actve = True,
            role = "admin",
        )
        db.add(admin)
        await db.commit()




async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())