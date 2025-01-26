from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.likes_juction_table import likes


class ImagePostModel(Base):
    __tablename__ = "image_posts"

    id: Mapped[int] = mapped_column(primary_key=True)  # PSQL gives an index to the pk by default
    image_url = Column(String, nullable=False)  # the URL of the image in CDN/ S3
    caption = Column(String, nullable=True)
    email_of_poster = Column(String)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    link_uuid = Column(
        String, index=True, nullable=True
    )  # don't store whole link, just uuid, create index for efficient lookup

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="image_posts")

    liked_by_users = relationship(
        "UserModel",
        secondary=likes,
        back_populates="liked_posts",
    )
