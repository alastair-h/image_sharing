from pydantic import BaseModel


class FollowUserRequest(BaseModel):
    follower_user_id: int  # the user.id of the user who wants to follow
    following_user_id: int  # the user.id of the user being followed
