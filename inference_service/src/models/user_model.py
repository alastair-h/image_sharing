from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.follows_junction_table import follows
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

    following_relationship = relationship(
        "UserModel",
        secondary=follows,
        primaryjoin=id == follows.c.follower,
        secondaryjoin=id == follows.c.following,
        backref="followers_relationship",
    )

    @property
    def following(self):  # TODO: maybe move towards a repository pattern with our Models
        # syntactic sugar
        return self.following_relationship
