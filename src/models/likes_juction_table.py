from sqlalchemy import Column, ForeignKey, Table

from src.models.base import Base

likes = Table(
    "likes",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),  # composite primary key
    Column("post_id", ForeignKey("image_posts.id"), primary_key=True),
)
