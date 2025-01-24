import http
from datetime import datetime
from http import HTTPStatus

from fastapi import FastAPI, Response, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from src.models.image_model import ImagePostModel
from src.models.user_model import UserModel

app = FastAPI()
DATABASE_URL = "postgresql+asyncpg://image_sharing_user:image_sharing_password@db:5432/image_sharing_db"


def get_async_engine() -> AsyncEngine:
    async_engine: AsyncEngine = create_async_engine(
        DATABASE_URL,
        future=True,
    )

    return async_engine


async def get_async_session():
    async_session = sessionmaker(
        bind=get_async_engine(),
        class_=AsyncSession,
        autoflush=False,
        expire_on_commit=False,  # TODO: understand this better
    )
    async with async_session() as async_sess:
        yield async_sess


class ImagePost(BaseModel):
    image_url: str
    caption: str = Field(..., max_length=100)
    timestamp: datetime
    email_of_poster: str  #


class User(BaseModel):
    username: str
    email: str


@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}


@app.post("/create_post", status_code=HTTPStatus.OK, responses={
    # HTTPStatus.OK: {"description": "OK - Post processed successfully"},  # always creates a new post
    HTTPStatus.CREATED: {"description": "Created - Post successfully created"},
}, )
async def image_post(image_post_data: ImagePost,
                     response: Response,
                     db: AsyncSession = Depends(get_async_session)) -> ImagePost:
    result = await db.execute(select(UserModel).where(UserModel.email == image_post_data.email_of_poster))
    user = result.scalars().one_or_none()
    if not user:
        response.status_code = HTTPStatus.BAD_REQUEST
        return {"detail": "User not found"}

    new_image = ImagePostModel(image_url=image_post_data.image_url,
                           caption=image_post_data.caption,
                           email_of_poster=image_post_data.email_of_poster,
                           user_id=user.id,
                           timestamp=image_post_data.timestamp)
    db.add(new_image)
    await db.commit()
    response.status_code = http.HTTPStatus.CREATED
    return image_post_data


@app.post("/signup_user", status_code=HTTPStatus.OK, responses={
    HTTPStatus.CREATED: {"description": "Created - user successfully created"},
}, )
async def user_signup(user_data: User,
                      response: Response,
                      db: AsyncSession = Depends(get_async_session)) -> User:
    new_user = UserModel(
        username=user_data.username,
        email=user_data.email,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    response.status_code = HTTPStatus.CREATED
    return new_user
