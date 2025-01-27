from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user_model import UserModel


class UserRepository:

    @staticmethod
    async def create_user(username: str, email: str, db: AsyncSession) -> UserModel:
        new_user = UserModel(username=username, email=email)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    @staticmethod
    async def get_user_by_email(email: str, db: AsyncSession) -> UserModel | None:
        result = await db.execute(select(UserModel).where(UserModel.email == email))
        return result.scalars().one_or_none()

    @staticmethod
    async def get_user_id_by_email(email: str, db: AsyncSession) -> int | None:
        result = await db.execute(select(UserModel.id).where(UserModel.email == email))
        return result.scalars().one_or_none()

    @staticmethod
    async def get_email_id_by_id(id: int, db: AsyncSession) -> str | None:
        result = await db.execute(select(UserModel.email).where(UserModel.id == id))
        return result.scalars().one_or_none()

    @staticmethod
    async def get_user_by_id(user_id: int, db: AsyncSession) -> UserModel | None:
        result = await db.execute(select(UserModel).where(UserModel.id == user_id))
        return result.scalars().one_or_none()
