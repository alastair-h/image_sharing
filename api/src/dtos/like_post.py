from pydantic import BaseModel


class LikePost(BaseModel):
    post_id: int
    user_id: int
