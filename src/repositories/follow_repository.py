from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.follows_junction_table import follows


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
