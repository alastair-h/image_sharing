from datetime import datetime

from pydantic import BaseModel, Field


class ImagePost(BaseModel):
    image_url: str
    caption: str = Field(..., max_length=100)
    timestamp: datetime
    email_of_poster: str  # TODO: add ID ?
