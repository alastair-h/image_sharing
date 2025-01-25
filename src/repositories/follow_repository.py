from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.follows_junction_table import follows
from src.models.user_model import UserModel


class FollowRepository:
    @staticmethod
    async def follow_user(follower_id: int, following_id: int, db: AsyncSession) -> None:
        await db.execute(follows.insert().values(follower=follower_id, following=following_id))
        await db.commit()

    @staticmethod
    async def is_following(follower_id: int, following_id: int, db: AsyncSession) -> bool:
        result = await db.execute(
            select(follows).where(follows.c.follower == follower_id, follows.c.following == following_id)
        )
        return result.fetchone() is not None

    @staticmethod
    async def get_list_users_user_is_following(user_id: int, db: AsyncSession) -> List[UserModel]:
        result = await db.execute(
            select(UserModel).join(follows, UserModel.id == follows.c.following).where(follows.c.follower == user_id)
        )
        return result.scalars().all()

    @staticmethod
    async def get_list_user_ids_following_user(user_id: int, db: AsyncSession) -> List[int]:
        result = await db.execute(select(follows).where(follows.c.following == user_id))
        return result.scalars().all()

    @staticmethod
    async def get_number_of_followers(user_id: int, db: AsyncSession) -> int:
        result = await db.execute(select(func.count()).select_from(follows).where(follows.c.following == user_id))
        return result.scalar() or 0

    @staticmethod
    async def get_number_of_following(user_id: int, db: AsyncSession) -> int:
        result = await db.execute(select(func.count()).select_from(follows).where(follows.c.follower == user_id))
        return result.scalar() or 0

    @staticmethod
    async def get_list_following_ids(user_id: int, db: AsyncSession) -> List[int]:
        result = await db.execute(select(follows.c.following).where(follows.c.follower == user_id))
        return result.scalars().all()
