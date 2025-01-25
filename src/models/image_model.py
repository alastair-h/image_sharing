from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.likes_juction_table import likes


class ImagePostModel(Base):
    __tablename__ = "image_posts"

    id: Mapped[int] = mapped_column(primary_key=True)  # PSQL gives an index to the pk by default
    image_url = Column(String, nullable=False)  # the URL of the image in CDN/ S3
    caption = Column(String, nullable=True)
    email_of_poster = Column(String)  # TODO: delete, unneeded denormalization
    timestamp = Column(DateTime(timezone=True), nullable=False)
    link_uuid = Column(String, index=True, nullable=True)  # don't store whole link, create index for efficient lookup

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Relationship back to User
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="image_posts")

    liked_by_users = relationship(
        "UserModel",
        secondary=likes,  # Reference to the association table
        back_populates="liked_posts",
    )
