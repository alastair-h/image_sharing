from pydantic import BaseModel


class FollowUserRequest(BaseModel):
    follower_user_email: str  # the user.id of the user who wants to follow
    following_user_email: str  # the user.id of the user being followed
