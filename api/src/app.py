from http import HTTPStatus
from typing import Dict, List

from fastapi import Depends, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.db.database import get_async_session
from src.dtos.follow_request import FollowUserRequest
from src.dtos.image_post import ImagePost
from src.dtos.like_post import LikePost
from src.dtos.user import User
from src.dtos.user_profile import UserProfile
from src.models.user_model import UserModel
from src.repositories.follow_repository import FollowRepository
from src.repositories.image_post_repository import ImagePostRepository
from src.repositories.like_repository import LikeRepository
from src.repositories.user_repository import UserRepository

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # needed to return 400 not 422, as per the spec
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


@app.post("/create_post", status_code=HTTPStatus.CREATED)
async def image_post(image_post_data: ImagePost, db: AsyncSession = Depends(get_async_session)) -> ImagePost:
    user_id = await UserRepository.get_user_id_by_email(image_post_data.email_of_poster, db)
    if not user_id:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="User not found")  # TODO: 404?

    new_post = await ImagePostRepository.create_post(
        image_url=image_post_data.image_url,
        caption=image_post_data.caption,
        email_of_poster=image_post_data.email_of_poster,
        user_id=user_id,
        timestamp=image_post_data.timestamp,
        db=db,
    )  # TODO: consider whether to return the whole post including id
    return new_post


@app.post("/signup_user", status_code=HTTPStatus.CREATED)
async def user_signup(user_data: User, db: AsyncSession = Depends(get_async_session)) -> User:
    new_user = await UserRepository.create_user(user_data.username, user_data.email, db)
    return new_user


@app.get("/get_posts/{email}", status_code=HTTPStatus.OK)  # consider use email
async def get_posts(email: str, db: AsyncSession = Depends(get_async_session)):
    user_id = await UserRepository.get_user_id_by_email(email, db)
    posts = await ImagePostRepository.get_posts_by_user_id(user_id, db)
    if not posts:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="No posts found")
    return posts


@app.put("/like_post", status_code=HTTPStatus.OK)
async def like_post(like_data: LikePost, db: AsyncSession = Depends(get_async_session)):
    post_exists = await ImagePostRepository.try_get_post_by_id(like_data.post_id, db)
    if not post_exists:
        return {"detail": "Post not found", "status_code": HTTPStatus.NOT_FOUND}
    user_id = await UserRepository.get_user_id_by_email(like_data.user_email, db)
    if not user_id:
        return {"detail": "User not found", "status_code": HTTPStatus.NOT_FOUND}
    if await LikeRepository.is_post_liked(like_data.post_id, user_id, db):
        return {"detail": "Post already liked"}
    await LikeRepository.like_post(like_data.post_id, user_id, db)
    return {"detail": "Post liked"}


@app.put("/unlike_post", status_code=HTTPStatus.OK)
async def unlike_post(unlike_data: LikePost, db: AsyncSession = Depends(get_async_session)):
    post_exists = await ImagePostRepository.try_get_post_by_id(unlike_data.post_id, db)
    if not post_exists:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="post not found")
    user_id = await UserRepository.get_user_id_by_email(unlike_data.user_email, db)
    if not user_id:
        return {"detail": "User not found", "status_code": HTTPStatus.NOT_FOUND}
    await LikeRepository.unlike_post(unlike_data.post_id, user_id, db)
    return {"detail": "Post unliked"}


@app.put("/follow_user", status_code=HTTPStatus.OK)
async def follow_user(follow_user_request: FollowUserRequest, db: AsyncSession = Depends(get_async_session)):
    follower_user_id = await UserRepository.get_user_id_by_email(follow_user_request.follower_user_email, db)
    following_user_id = await UserRepository.get_user_id_by_email(follow_user_request.following_user_email, db)
    if not await UserRepository.get_user_by_id(follower_user_id, db):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Follower user not found")
    if not await UserRepository.get_user_by_id(following_user_id, db):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Following user not found")
    if await FollowRepository.is_following(follower_id=follower_user_id, following_id=following_user_id, db=db):
        return {"detail": "Already following"}
    await FollowRepository.follow_user(follower_id=follower_user_id, following_id=following_user_id, db=db)
    return {"detail": "Followed successfully"}


@app.get("/get_following_list/{email}", status_code=HTTPStatus.OK)
async def get_following_list(email: str, db: AsyncSession = Depends(get_async_session)) -> List[Dict]:
    # get a list of everyone this user is following
    user_id = await UserRepository.get_user_id_by_email(email, db)
    following_list = await FollowRepository.get_list_users_user_is_following(user_id, db)
    following_list_without_id = [User.from_db_model(user) for user in following_list]
    return {"following": following_list_without_id}


@app.get("/user_profile")
async def get_user_profile(email: str, db: AsyncSession = Depends(get_async_session)) -> UserProfile:
    user: UserModel = await UserRepository.get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="user not found")
    following_count = await FollowRepository.get_number_of_following(user.id, db)
    follower_count = await FollowRepository.get_number_of_followers(user.id, db)

    return UserProfile(user=User.from_db_model(user), following_count=following_count, follower_count=follower_count)


@app.get("/get_posts_from_user/{email}", status_code=HTTPStatus.OK)
async def get_posts_from_user(email: str, db: AsyncSession = Depends(get_async_session)):
    user_id = await UserRepository.get_user_id_by_email(email, db)
    get_all_posts_for_user = await ImagePostRepository.get_all_posts_for_user(db, user_id)
    return {"posts": get_all_posts_for_user}


@app.get("/get_posts_from_following/{email}", status_code=HTTPStatus.OK)
async def get_posts_from_following(email: str, db: AsyncSession = Depends(get_async_session)):
    user_id = await UserRepository.get_user_id_by_email(email, db)
    following_ids = await FollowRepository.get_list_following_ids(user_id, db)
    if not following_ids:
        return {"posts": []}

    posts = await ImagePostRepository.get_all_posts(db, following_ids)
    sorted_list = sorted(posts, key=lambda x: x.timestamp, reverse=True)
    return {"posts": sorted_list}


@app.get("/get_most_liked_posts", status_code=HTTPStatus.OK)
async def get_most_liked_posts(db: AsyncSession = Depends(get_async_session)):
    """
    > List posts from followed users (sorted by most recent) and all posts (sorted
    by number of likes).
    >  and all posts (sorted by number of likes).
    I take this to mean created a list of most liked posts across all users.

    I intentionally don't return the number of likes for each post: I imagine this to be used to make a 'trending' page
    """
    posts = await LikeRepository.get_most_liked_posts(db)
    return {"most_liked_posts": posts}


@app.get("/get_mutual_followers/{email_1}/{email_2}", status_code=HTTPStatus.OK)
async def get_mutual_followers(
    email_1: str, email_2: str, db: AsyncSession = Depends(get_async_session)
):  # TODO: create dto
    """
    d. Show mutual followers (users who follow both the viewer and the profile
    owner) and suggest followers based on mutual connections.
    """
    user_id_1 = await UserRepository.get_user_id_by_email(email_1, db)
    user_id_2 = await UserRepository.get_user_id_by_email(email_2, db)
    users_following_user_1 = await FollowRepository.get_list_user_ids_following_user(user_id_1, db)
    users_following_user_2 = await FollowRepository.get_list_user_ids_following_user(user_id_2, db)
    common = [x for x in users_following_user_1 if x in users_following_user_2]
    common_emails = [await UserRepository.get_email_id_by_id(user_id, db) for user_id in common]
    return {"mutual followers": common_emails}


@app.get("/get_sharable_link/{post_id}", status_code=HTTPStatus.CREATED)
async def get_sharable_link(post_id: int, db: AsyncSession = Depends(get_async_session)) -> str:
    post = await ImagePostRepository.try_get_post_by_id(post_id, db)
    if not post:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found")

    return await ImagePostRepository.publish_post(post_id, db)


@app.get("/posts/{post_uuid}", status_code=HTTPStatus.OK)
async def get_post_by_public_link(post_uuid: str, db: AsyncSession = Depends(get_async_session)) -> ImagePost:
    if len(post_uuid) != 36:  # TODO: maybe use pydantic for validation this as per other requests
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Invalid UUID format")
    image_post = await ImagePostRepository.try_get_published_post_by_uuid(post_uuid, db)
    if image_post:
        return image_post
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Post not found")
