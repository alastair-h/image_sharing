import uuid
from datetime import datetime
from http import HTTPStatus

from src.models.image_model import ImagePostModel
from src.models.user_model import UserModel


def test_get_sharable_link_success(client, db_session):
    user = UserModel(username="user", email="user@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    post = ImagePostModel(image_url="http://example.com/image.jpg", caption="Test Post", timestamp=datetime(2025, 1, 1), user_id=user.id)
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    response = client.get(f"/get_sharable_link/{post.id}")

    assert response.status_code == HTTPStatus.CREATED
    sharable_link = response.json()
    assert sharable_link.startswith("https://app.com/posts/")
    assert len(sharable_link.split("/")[-1]) == 36  # check there is a UUID at end of link


def test_get_sharable_link_post_not_found(client, db_session):
    response = client.get("/get_sharable_link/999")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Post not found"}


def test_get_post_by_public_link_success(client, db_session):
    user = UserModel(username="test_user", email="test_user@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    post = ImagePostModel(
        image_url="http://example.com/image.jpg",
        caption="Test Post",
        link_uuid=str(uuid.uuid4()),
        user_id=user.id,
        timestamp=datetime.now()
    )
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    response = client.get(f"/posts/{post.link_uuid}")

    assert response.status_code == HTTPStatus.OK
    post_data = response.json()
    assert post_data["image_url"] == "http://example.com/image.jpg"
    assert post_data["caption"] == "Test Post"

def test_get_post_by_public_link_not_found(client, db_session):
    non_existent_uuid = str(uuid.uuid4())
    response = client.get(f"/posts/{non_existent_uuid}")

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Post not found"}

def test_get_post_by_public_link_invalid_uuid(client):
    response = client.get("/posts/invalid-uuid-format")

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "Invalid UUID format"}
