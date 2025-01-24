from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class ImagePostModel(Base):
    __tablename__ = "image_posts"

    id: Mapped[int] = mapped_column(primary_key=True)  # PSQL gives an index to the pk by default
    image_url = Column(String)
    caption = Column(String)
    email_of_poster = Column(String)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationship back to User
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="image_posts"
    )

