from pydantic import BaseModel

from src.dtos.user import User


class UserProfile(BaseModel):
    user: User
    following_count: int
    follower_count: int
