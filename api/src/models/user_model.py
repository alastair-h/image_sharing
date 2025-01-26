from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.follows_junction_table import follows
from src.models.likes_juction_table import likes


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)  # since we are exposing this via API it is better to use UUID
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)  # index for faster lookup

    image_posts: Mapped[list["ImagePostModel"]] = relationship(
        "ImagePostModel", back_populates="user", cascade="all, delete-orphan"
    )

    liked_posts = relationship(
        "ImagePostModel",
        secondary=likes,  #  association table
        back_populates="liked_by_users",
    )

    following = relationship(
        "UserModel",
        secondary=follows,
        primaryjoin=id == follows.c.follower,
        secondaryjoin=id == follows.c.following,
        backref="followers_relationship",
    )
