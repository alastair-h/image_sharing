import uuid
from typing import List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.image_model import ImagePostModel


class ImagePostRepository:
    @staticmethod
    async def create_post(image_url: str, caption: str, email_of_poster: str, user_id: int, timestamp,
                          db: AsyncSession) -> ImagePostModel:
        new_image = ImagePostModel(
            image_url=image_url,
            caption=caption,
            email_of_poster=email_of_poster,
            user_id=user_id,
            timestamp=timestamp
        )
        db.add(new_image)
        await db.commit()
        await db.refresh(new_image)
        return new_image

    @staticmethod
    async def get_posts_by_user_id(user_id: int, db: AsyncSession) -> List[ImagePostModel]:
        result = await db.execute(select(ImagePostModel).where(ImagePostModel.user_id == user_id))
        return result.scalars().all()


    @staticmethod
    async def get_post_by_id(post_id: int, db: AsyncSession) -> ImagePostModel:
        result = await db.execute(select(ImagePostModel).where(ImagePostModel.id == post_id))
        return result.scalars().first()

    @staticmethod
    async def try_get_post_by_id(post_id: int, db: AsyncSession) -> ImagePostModel | None:
        result = await db.execute(select(ImagePostModel).where(ImagePostModel.id == post_id))
        return result.scalars().one_or_none()

    @staticmethod
    async def get_all_posts_for_user(db: AsyncSession, user_id: int) -> List[ImagePostModel]:
        result = await db.execute(select(ImagePostModel).where(ImagePostModel.user_id == user_id))
        return result.scalars().all()

    @staticmethod
    async def get_all_posts(db: AsyncSession, user_ids: List[int]) -> list[ImagePostModel]:
        result = await db.execute(
            select(ImagePostModel)
            .where(ImagePostModel.user_id.in_(user_ids))
            .order_by(ImagePostModel.timestamp.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def publish_post(post_id: int, db: AsyncSession) -> str:
        # Generate a UUID
        new_uuid = str(uuid.uuid4())

        # Update the post with the generated UUID
        await db.execute(
            update(ImagePostModel)
            .where(ImagePostModel.id == post_id)
            .values(link_uuid=new_uuid)
        )
        await db.commit()

        # Return the shareable link
        return f"https://app.com/posts/{new_uuid}"

    @staticmethod
    async def try_get_published_post_by_uuid(post_uuid: str, db: AsyncSession) -> ImagePostModel | None:
        post = await db.execute(
            select(ImagePostModel).where(ImagePostModel.link_uuid == post_uuid)
        )
        return post.scalars().one_or_none()

