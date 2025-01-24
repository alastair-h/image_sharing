from sqlalchemy import Column, Integer, String

from src.models.base import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)  # PSQL gives an index to the pk by default
    image_url = Column(String)
    caption = Column(String)

