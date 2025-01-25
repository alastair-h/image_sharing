from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.likes_juction_table import likes


class LikeRepository:
    @staticmethod
    async def like_post(post_id: int, user_id: int, db: AsyncSession) -> None:
        await db.execute(likes.insert().values(post_id=post_id, user_id=user_id))
        await db.commit()

    @staticmethod
    async def is_post_liked(post_id: int, user_id: int, db: AsyncSession) -> bool:
        result = await db.execute(
            select(likes).where(
                likes.c.post_id == post_id,
                likes.c.user_id == user_id
            )
        )
        return result.fetchone() is not None
