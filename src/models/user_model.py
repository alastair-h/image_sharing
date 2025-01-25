from typing import List

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.models.base import Base
from src.models.likes_juction_table import likes


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # Relationship back to ImagePosts
    # 'back_populates' must match the 'user' relationship in ImagePost
    image_posts: Mapped[list["ImagePostModel"]] = relationship(
        "ImagePostModel", back_populates="user", cascade="all, delete-orphan"
    )

    liked_posts = relationship(
        "ImagePostModel",
        secondary=likes,  # Reference to the association table
        back_populates="liked_by_users",
    )