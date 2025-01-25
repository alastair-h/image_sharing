from datetime import datetime, timezone
from http import HTTPStatus

from sqlalchemy import text

from src.models.image_model import ImagePostModel
from src.models.user_model import UserModel


def test_post_image(client, db_session) -> None:
    user_data = {"username": "test_user", "email": "testuser@example.org"}
    response = client.post(
        "/signup_user",
        headers={"content-type": "application/json"},
        json=user_data,
    )
    assert response.status_code == HTTPStatus.CREATED
    image_post_data = {"image_url": "https://www.example.com/image.jpg",
                       "caption": "A caption",
                       "email_of_poster": "testuser@example.org",
                       "timestamp": datetime.now(timezone.utc).isoformat()}
    response = client.post(
        "/create_post",
        headers={"content-type": "application/json"},
        json=image_post_data,
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == image_post_data

    # Query the database to verify the item was inserted
    result = db_session.execute(text("SELECT image_url, caption FROM image_posts"))
    inserted_item = result.fetchone()

    assert inserted_item is not None
    assert inserted_item.image_url == image_post_data["image_url"]
    assert inserted_item.caption == image_post_data["caption"]


def test_too_long_caption_raises_error(client, db_session) -> None:
    user_data = {"username": "test_user", "email": "testuser@example.org"}  # TODO: move to fixture, use db directly
    client.post(
        "/signup_user",
        headers={"content-type": "application/json"},
        json=user_data,
    )

    image_post_data = {"image_url": "https://www.example.com/second-image.jpg",
                       "caption": "very long caption" * 10,
                       "email_of_poster": "testuser@example.org",
                       "timestamp": datetime.now(timezone.utc).isoformat()}
    response = client.post(
        "/create_post",
        headers={"content-type": "application/json"},
        json=image_post_data,
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': [
        {'loc': ['body', 'caption'], 'msg': 'ensure this value has at most 100 characters',
         'type': 'value_error.any_str.max_length', 'ctx': {'limit_value': 100}}]}

    # Query the database to verify the item was not inserted
    result = db_session.execute(text("SELECT image_url, caption FROM image_posts"))
    assert result.fetchone() is None


def test_user_not_found(client, db_session) -> None:
    image_post_data = {"image_url": "https://www.example.com/image.jpg",
                       "caption": "A caption",
                       "email_of_poster": "unfound@nonexistant.com",
                       "timestamp": datetime.now(timezone.utc).isoformat()}
    response = client.post(
        "/create_post",
        headers={"content-type": "application/json"},
        json=image_post_data,
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_no_timestamp_raises_error(client, db_session) -> None:
    user_data = {"username": "test_user",
                 "email": "testuser@example.org"}  # TODO: move to fixture, use db directly

    client.post(
        "/signup_user",
        headers={"content-type": "application/json"},
        json=user_data,
    )

    image_post_data = {"image_url": "https://www.example.com/image.jpg",
                       "caption": "A caption",
                       "email_of_poster": "unfound@nonexistant.com"}

    response = client.post(
        "/create_post",
        headers={"content-type": "application/json"},
        json=image_post_data,
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_get_posts(client, db_session):
    user = UserModel(username="test_user", email="test_user@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)  # Ensure `id` is populated

    post1 = ImagePostModel(image_url="http://example.com/image1.jpg", caption="First Post", user_id=user.id, timestamp=datetime.now(timezone.utc))
    post2 = ImagePostModel(image_url="http://example.com/image2.jpg", caption="Second Post", user_id=user.id,  timestamp=datetime.now(timezone.utc))

    db_session.add_all([post1, post2])
    db_session.commit()

    response = client.get(f"/get_posts/{user.id}")

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()

    assert len(response_data) == 2

    assert any(post["image_url"] == "http://example.com/image1.jpg" for post in response_data)
    assert any(post["image_url"] == "http://example.com/image2.jpg" for post in response_data)
    assert any(post["caption"] == "First Post" for post in response_data)
    assert any(post["caption"] == "Second Post" for post in response_data)
