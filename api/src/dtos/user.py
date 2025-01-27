from typing import Self

from pydantic import BaseModel

from src.models.user_model import UserModel


class User(BaseModel):
    username: str
    email: str

    @staticmethod
    def from_db_model(user_db_model: UserModel) -> Self:
        return User(username=user_db_model.username, email=user_db_model.email)
