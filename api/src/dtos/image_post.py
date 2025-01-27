from datetime import datetime
from typing import Optional, Self

from pydantic import BaseModel, Field

from src.models.image_model import ImagePostModel


class ImagePost(BaseModel):
    image_url: str
    caption: Optional[str] = Field(..., max_length=100)
    timestamp: datetime
    email_of_poster: str

    @staticmethod
    def from_db_model(image_post_db_model: ImagePostModel) -> Self:
        return ImagePost(
            image_url=image_post_db_model.image_url,
            caption=image_post_db_model.caption,
            timestamp=image_post_db_model.timestamp,
            email_of_poster=image_post_db_model.email_of_poster,
        )
