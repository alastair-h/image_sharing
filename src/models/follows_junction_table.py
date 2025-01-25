from sqlalchemy import Column, ForeignKey, Table

from src.models.base import Base

follows = Table(
    "follows",
    Base.metadata,
    Column("follower", ForeignKey("users.id"), primary_key=True),  # composite primary key
    Column("following", ForeignKey("users.id"), primary_key=True),
)
