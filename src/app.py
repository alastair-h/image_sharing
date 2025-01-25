from datetime import datetime
from http import HTTPStatus

from fastapi import FastAPI, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request

from src.dtos.image_post import ImagePost
from src.repositories.follow_repository import FollowRepository
from src.repositories.image_post_repository import ImagePostRepository
from src.repositories.like_repository import LikeRepository
from src.repositories.user_repository import UserRepository

app = FastAPI()
DATABASE_URL = "postgresql+asyncpg://image_sharing_user:image_sharing_password@db:5432/image_sharing_db"


def get_async_engine() -> AsyncEngine:  # TODO: review this, are we making an engine for each request?
    # does fast api provide a singleton pattern here?
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
        expire_on_commit=False,
    )
    async with async_session() as async_sess:
        yield async_sess


class User(BaseModel):
    username: str
    email: str


class LikePost(BaseModel):
    post_id: int
    user_id: int


class FollowUserRequest(BaseModel):
    follower_user_id: int  # the user.id of the user who wants to follow
    following_user_id: int  # the user.id of the user being followed


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # needed to return 400 not 422
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}


@app.post("/create_post", status_code=HTTPStatus.CREATED)
async def image_post(image_post_data: ImagePost, db: AsyncSession = Depends(get_async_session)) -> ImagePost:
    user = await UserRepository.get_user_by_email(image_post_data.email_of_poster, db)
    if not user:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User not found")

    new_post = await ImagePostRepository.create_post(
        image_url=image_post_data.image_url,
        caption=image_post_data.caption,
        email_of_poster=image_post_data.email_of_poster,
        user_id=user.id,
        timestamp=image_post_data.timestamp,
        db=db
    )  # TODO: consider whether to return the whole post including id
    return new_post


@app.post("/signup_user", status_code=HTTPStatus.CREATED)
async def user_signup(user_data: User, db: AsyncSession = Depends(get_async_session)) -> User:
    new_user = await UserRepository.create_user(user_data.username, user_data.email, db)
    return new_user


@app.get("/get_posts/{user_id}", status_code=HTTPStatus.OK)
async def get_posts(user_id: int, db: AsyncSession = Depends(get_async_session)):
    posts = await ImagePostRepository.get_posts_by_user_id(user_id, db)
    if not posts:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="No posts found")
    return posts


@app.put("/like_post", status_code=HTTPStatus.OK)
async def like_post(like_data: LikePost, db: AsyncSession = Depends(get_async_session)):
    if await LikeRepository.is_post_liked(like_data.post_id, like_data.user_id, db):
        return {"detail": "Post already liked"}
    await LikeRepository.like_post(like_data.post_id, like_data.user_id, db)
    return {"detail": "Post liked"}


@app.put("/follow_user", status_code=HTTPStatus.OK)  # TODO: look at how auth changes the scope of this
async def follow_user(follow_user_request: FollowUserRequest, db: AsyncSession = Depends(get_async_session)):
    if await FollowRepository.is_following(follow_user_request.follower_user_id, follow_user_request.following_user_id, db):
        return {"detail": "Already following"}
    await FollowRepository.follow_user(follow_user_request.follower_user_id, follow_user_request.following_user_id, db)
    return {"detail": "Followed successfully"}

