from http import HTTPStatus
from typing import Self

from fastapi import Depends, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request

from src.dtos.image_post import ImagePost
from src.models.user_model import UserModel
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


class User(
    BaseModel
):  # TODO: think about whether to expose ID to frontend, mostly working with IDs, but don't want to expose implementation
    username: str  # TODO: could use hash
    email: str

    @staticmethod
    def from_db_model(user_db_model: UserModel) -> Self:
        return User(username=user_db_model.username, email=user_db_model.email)


class UserProfile(BaseModel):
    user: User
    following_count: int
    follower_count: int


class LikePost(BaseModel):
    post_id: int
    user_id: int


class FollowUserRequest(BaseModel):
    follower_user_id: int  # the user.id of the user who wants to follow
    following_user_id: int  # the user.id of the user being followed


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # needed to return 400 not 422, as per the spec
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
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User not found")  # TODO: 404?

    new_post = await ImagePostRepository.create_post(
        image_url=image_post_data.image_url,
        caption=image_post_data.caption,
        email_of_poster=image_post_data.email_of_poster,
        user_id=user.id,
        timestamp=image_post_data.timestamp,
        db=db,
    )  # TODO: consider whether to return the whole post including id
    return new_post


@app.post("/signup_user", status_code=HTTPStatus.CREATED)
async def user_signup(user_data: User, db: AsyncSession = Depends(get_async_session)) -> User:
    new_user = await UserRepository.create_user(user_data.username, user_data.email, db)
    return new_user


@app.get("/get_posts/{user_id}", status_code=HTTPStatus.OK)  # todo: rename to get_posts_by_user_id
async def get_posts(user_id: int, db: AsyncSession = Depends(get_async_session)):
    posts = await ImagePostRepository.get_posts_by_user_id(user_id, db)
    if not posts:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="No posts found")
    return posts


@app.put("/like_post", status_code=HTTPStatus.OK)
async def like_post(like_data: LikePost, db: AsyncSession = Depends(get_async_session)):
    post_exists = await ImagePostRepository.try_get_post_by_id(like_data.post_id, db)
    if not post_exists:
        return {"detail": "Post not found", "status_code": HTTPStatus.NOT_FOUND}
    if await LikeRepository.is_post_liked(like_data.post_id, like_data.user_id, db):
        return {"detail": "Post already liked"}  # TODO: get rid of, its a put
    await LikeRepository.like_post(like_data.post_id, like_data.user_id, db)
    return {"detail": "Post liked"}


@app.put("/unlike_post", status_code=HTTPStatus.OK)
async def unlike_post(unlike_data: LikePost, db: AsyncSession = Depends(get_async_session)):
    post_exists = await ImagePostRepository.try_get_post_by_id(unlike_data.post_id, db)
    if not post_exists:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="post not found")
    await LikeRepository.unlike_post(unlike_data.post_id, unlike_data.user_id, db)
    return {"detail": "Post unliked"}


@app.put("/follow_user", status_code=HTTPStatus.OK)
async def follow_user(follow_user_request: FollowUserRequest, db: AsyncSession = Depends(get_async_session)):
    if not await UserRepository.get_user_by_id(follow_user_request.follower_user_id, db):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Follower user not found")
    if await FollowRepository.is_following(
        follow_user_request.follower_user_id, follow_user_request.following_user_id, db
    ):
        return {"detail": "Already following"}
    await FollowRepository.follow_user(follow_user_request.follower_user_id, follow_user_request.following_user_id, db)
    return {"detail": "Followed successfully"}

@app.get("/get_following_list/{user_id}", status_code=HTTPStatus.OK)  # TODO: rename remove get
async def get_following_list(user_id: int, db: AsyncSession = Depends(get_async_session)):
    # get a list of everyone this user is following
    following_list = await FollowRepository.get_list_users_user_is_following(user_id, db)
    return {"following": following_list}


@app.get("/user_profile")
async def get_user_profile(user_id: int, db: AsyncSession = Depends(get_async_session)) -> UserProfile:
    user: UserModel = await UserRepository.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="user not found")
    following_count = await FollowRepository.get_number_of_following(user_id, db)
    follower_count = await FollowRepository.get_number_of_followers(user_id, db)

    return UserProfile(user=User.from_db_model(user), following_count=following_count, follower_count=follower_count)


@app.get("/get_posts_from_user/{user_id}", status_code=HTTPStatus.OK)
async def get_posts_from_user(user_id: int, db: AsyncSession = Depends(get_async_session)):
    get_all_posts_for_user = await ImagePostRepository.get_all_posts_for_user(db, user_id)
    return {"posts": get_all_posts_for_user}


@app.get("/get_posts_from_following/{user_id}", status_code=HTTPStatus.OK)
async def get_posts_from_following(user_id: int, db: AsyncSession = Depends(get_async_session)):
    following_ids = await FollowRepository.get_list_following_ids(user_id, db)
    if not following_ids:
        return {"posts": []}

    posts = await ImagePostRepository.get_all_posts(db, following_ids)
    sorted_list = sorted(posts, key=lambda x: x.timestamp, reverse=True)
    return {"posts": sorted_list}


"""
List posts from followed users (sorted by most recent) and all posts (sorted
by number of likes).

>  and all posts (sorted
by number of likes).

I take this to mean created a list of most liked posts across all users
"""


@app.get("/get_most_liked_posts", status_code=HTTPStatus.OK)
async def get_most_liked_posts(db: AsyncSession = Depends(get_async_session)):
    """
    > List posts from followed users (sorted by most recent) and all posts (sorted
    by number of likes).
    >  and all posts (sorted by number of likes).
    I take this to mean created a list of most liked posts across all users.

    I intentionally don't return the number of likes for each post: I imagine this to be used to make a 'trending' page
    """

    # TODO: look into the efficiency of this because its a lot of data. we might need to denormalize the data
    # we also should consider pagination, using a limit properly

    # should just get the table likes, and the count of likes for each post
    posts = await LikeRepository.get_most_liked_posts(db)
    return {"most_liked_posts": posts}


@app.get("/get_mutual_followers/{user_id_1}/{user_id_2}", status_code=HTTPStatus.OK)
async def get_mutual_followers(user_id_1: int, user_id_2: int, db: AsyncSession = Depends(get_async_session)):
    """
    d. Show mutual followers (users who follow both the viewer and the profile
    owner) and suggest followers based on mutual connections.
    """
    users_following_user_1 = await FollowRepository.get_list_user_ids_following_user(user_id_1, db)
    users_following_user_2 = await FollowRepository.get_list_user_ids_following_user(user_id_2, db)
    common = [x for x in users_following_user_1 if x in users_following_user_2]
    return {"mutual followers": common}


async def get_suggested_users():
    """
    given user a, user b, user c user d, user e, user f

    user a follows user b, and user d also follows user b.
    user e follows user c.
    user f follows user b.
    users a, d, f should be more likely to follow each other,
    vs user e or user c, who seemingly have no relation

    TODO: to me, suggested follower is the same as mutual followers unless we are looking to delve into graph theory here.
    suggestions based on mutual followers with one node of depth is already provided in get_mutual_followers.
    """
    pass


@app.get("/get_sharable_link/{post_id}", status_code=HTTPStatus.CREATED)
async def get_sharable_link(post_id: int, db: AsyncSession = Depends(get_async_session)) -> str:
    post = await ImagePostRepository.try_get_post_by_id(post_id, db)
    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found")

    return await ImagePostRepository.publish_post(post_id, db)


@app.get("/posts/{post_uuid}", status_code=HTTPStatus.OK)
async def get_post_by_public_link(post_uuid: str, db: AsyncSession = Depends(get_async_session)) -> ImagePost:
    if len(post_uuid) != 36:  # TODO: maybe use pydantic for this as per other requests
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid UUID format")
    image_post = await ImagePostRepository.try_get_published_post_by_uuid(post_uuid, db)
    if image_post:
        return image_post
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found")
