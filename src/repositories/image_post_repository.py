from sqlalchemy import select
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
    async def get_posts_by_user_id(user_id: int, db: AsyncSession) -> list[ImagePostModel]:
        result = await db.execute(select(ImagePostModel).where(ImagePostModel.user_id == user_id))
        return result.scalars().all()
