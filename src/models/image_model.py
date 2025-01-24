from sqlalchemy import Column, Integer, String, DateTime

from src.models.base import Base
from sqlalchemy import Column, Integer, String, DateTime

from src.models.base import Base


class ImageModel(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)  # PSQL gives an index to the pk by default
    image_url = Column(String)
    caption = Column(String)
    timestamp = Column(DateTime(timezone=True), nullable=False)

