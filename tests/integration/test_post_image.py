from datetime import datetime, timezone
from http import HTTPStatus

from sqlalchemy import text


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
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
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
    user_data = {"username": "test_user", "email": "testuser@example.org"}  # TODO: move to fixture, use db directly
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

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
