from datetime import datetime
from http import HTTPStatus

from fastapi import FastAPI, Response, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request

from src.models.follows_junction_table import follows
from src.models.image_model import ImagePostModel
from src.models.likes_juction_table import likes
from src.models.user_model import UserModel

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


@app.post("/create_post", status_code=HTTPStatus.CREATED, )
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
    return image_post_data


@app.post("/signup_user", status_code=HTTPStatus.CREATED)
async def user_signup(user_data: User,
                      db: AsyncSession = Depends(get_async_session)) -> User:
    new_user = UserModel(
        username=user_data.username,
        email=user_data.email,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@app.get("/get_posts/{user_id}", status_code=HTTPStatus.OK, responses={
    HTTPStatus.OK: {"model": ImagePost},
    HTTPStatus.NOT_FOUND: {"model": None}
})
async def get_posts(user_id: int,
                    db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(ImagePostModel).where(ImagePostModel.user_id == user_id))
    posts = result.scalars().all()
    if not posts:
        return None
    return posts


@app.put("/like_post", status_code=HTTPStatus.OK)
async def like_post(like_data: LikePost,
                    db: AsyncSession = Depends(get_async_session)):
    await db.execute(likes.insert().values(post_id=like_data.post_id, user_id=like_data.user_id))
    await db.commit()
    return {"detail": "Post liked"}


@app.put("/follow_user", status_code=HTTPStatus.OK)
async def follow_user(follow_user_request: FollowUserRequest,
                      db: AsyncSession = Depends(get_async_session)):
    # TODO: if implementing auth, check that the user is the same as the one in the token, maybe we can simplify this
    await db.execute(follows.insert().values(follower=follow_user_request.follower_user_id,
                                             following=follow_user_request.following_user_id))
    await db.commit()
    # TODO: 404 if user not found
