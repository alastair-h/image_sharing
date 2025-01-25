from datetime import datetime, timezone
from http import HTTPStatus

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.image_model import ImagePostModel
from src.models.user_model import UserModel


def test_get_posts_from_user(client, db_session: AsyncSession) -> None:
    # setup multiple users and posts. we can't use a fixutre because it would be truncated
    user1 = UserModel(username="user1", email="user1@example.com")
    user2 = UserModel(username="user2", email="user2@example.com")
    db_session.add_all([user1, user2])
    db_session.commit()
    db_session.refresh(user1)
    db_session.refresh(user2)

    posts_user1 = [
        ImagePostModel(image_url="http://example.com/image1.jpg", caption="Post 1", user_id=user1.id,
                       timestamp=datetime.now(timezone.utc)),
        ImagePostModel(image_url="http://example.com/image2.jpg", caption="Post 2", user_id=user1.id,
                       timestamp=datetime.now(timezone.utc)),
    ]
    posts_user2 = [
        ImagePostModel(image_url="http://example.com/image3.jpg", caption="Post 3", user_id=user2.id,
                       timestamp=datetime.now(timezone.utc)),
        ImagePostModel(image_url="http://example.com/image4.jpg", caption="Post 4", user_id=user2.id,
                       timestamp=datetime.now(timezone.utc)),
    ]
    db_session.add_all(posts_user1 + posts_user2)
    db_session.commit()

    # Act: Make a request to fetch posts for user1
    response = client.get(f"/get_posts_from_user/{user1.id}")

    # Assert: Ensure the response contains only posts from user1
    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert "posts" in response_data
    assert len(response_data["posts"]) == 2
    assert all(post["user_id"] == user1.id for post in response_data["posts"])
    expected_urls = ["http://example.com/image1.jpg", "http://example.com/image2.jpg"]
    returned_urls = [post["image_url"] for post in response_data["posts"]]
    assert set(returned_urls) == set(expected_urls)


def __setup_get_posts_from_following(passed_session: AsyncSession) -> UserModel:
    # the setup is so big I put it in a "fixture" function and pass the same session from the test
    user = UserModel(username="user", email="user@example.com")
    following_1 = UserModel(username="following1", email="following1@example.com")
    following_2 = UserModel(username="following2", email="following2@example.com")
    not_following = UserModel(username="not following", email="not following@example.com")
    passed_session.add_all([user, following_1, following_2, not_following])
    passed_session.commit()
    passed_session.refresh(user)
    passed_session.refresh(following_1)
    passed_session.refresh(following_2)
    passed_session.refresh(not_following)

    # Add follow relationships
    passed_session.execute(
        text("INSERT INTO follows (follower, following) VALUES (:follower, :following)"),
        {"follower": user.id, "following": following_1.id},
    )
    passed_session.execute(
        text("INSERT INTO follows (follower, following) VALUES (:follower, :following)"),
        {"follower": user.id, "following": following_2.id},
    )
    passed_session.commit()

    # Add posts for the followed users
    post1 = ImagePostModel(
        image_url="http://example.com/image1.jpg",
        caption="Post 1",
        user_id=following_1.id,
        timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )
    post2 = ImagePostModel(
        image_url="http://example.com/image2.jpg",
        caption="Post 2",
        user_id=following_2.id,
        timestamp=datetime(2025, 1, 2, tzinfo=timezone.utc),
    )

    post_3 = ImagePostModel(
        image_url="http://example.com/image3.jpg",
        caption="Post 3",
        user_id=not_following.id,
        timestamp=datetime(2025, 1, 3, tzinfo=timezone.utc))

    post_4 = ImagePostModel(
        image_url="http://example.com/image4.jpg",
        caption="Post 4",
        user_id=following_2.id,
        timestamp=datetime(2025, 1, 4, tzinfo=timezone.utc),
    )
    passed_session.add_all([post1, post2, post_3, post_4])
    passed_session.commit()
    return user


def test_get_posts_from_following_success(client, db_session: AsyncSession):
    user = __setup_get_posts_from_following(db_session)

    response = client.get(f"/get_posts_from_following/{user.id}")

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert "posts" in response_data
    assert len(response_data["posts"]) == 3
    assert response_data["posts"][0]["caption"] == "Post 4"  # Most recent post
    assert response_data["posts"][1]["caption"] == "Post 2"  # Older post
    assert response_data["posts"][2]["caption"] == "Post 1"  # Oldest post


