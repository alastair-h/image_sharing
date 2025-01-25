from typing import List

from sqlalchemy import select
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
            select(follows).where(
                follows.c.follower == follower_id,
                follows.c.following == following_id
            )
        )
        return result.fetchone() is not None

    @staticmethod
    async def get_list_following(user_id: int, db: AsyncSession) -> List[UserModel]:
        result = await db.execute(
            select(UserModel).join(follows, UserModel.id == follows.c.following).where(follows.c.follower == user_id)
        )
        return result.scalars().all()

    @staticmethod
    async def get_list_following_ids(user_id: int, db: AsyncSession) -> List[int]:
        result = await db.execute(
            select(follows.c.following).where(follows.c.follower == user_id)
        )
        return result.scalars().all()


