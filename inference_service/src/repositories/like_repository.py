from typing import List

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.likes_juction_table import likes


class LikeRepository:
    @staticmethod
    async def like_post(post_id: int, user_id: int, db: AsyncSession) -> None:
        await db.execute(likes.insert().values(post_id=post_id, user_id=user_id))
        await db.commit()

    @staticmethod
    async def unlike_post(post_id: int, user_id: int, db: AsyncSession) -> None:
        await db.execute(likes.delete().where(likes.c.post_id == post_id, likes.c.user_id == user_id))
        await db.commit()

    @staticmethod
    async def is_post_liked(post_id: int, user_id: int, db: AsyncSession) -> bool:
        result = await db.execute(select(likes).where(likes.c.post_id == post_id, likes.c.user_id == user_id))
        return result.fetchone() is not None

    @staticmethod
    async def get_most_liked_posts(db: AsyncSession, num_posts: int = 5) -> List[int]:
        # whilst it is surely possible to do this with the ORM I'm going to use raw SQL
        # as I can guarantee a simple query
        sql_statement = text(
            f"""
        
        SELECT post_id, COUNT(*) AS occurrence
        FROM likes GROUP BY post_id
        ORDER BY occurrence DESC
        LIMIT {num_posts};
        
        """
        )
        result = await db.execute(sql_statement)
        post_ids = [row[0] for row in result.fetchall()]
        return post_ids
