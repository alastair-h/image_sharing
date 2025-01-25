from datetime import datetime, timezone
from http import HTTPStatus

from sqlalchemy import text

from src.models.image_model import ImagePostModel
from src.models.user_model import UserModel


def test_like_post_success(client, db_session) -> None:
    user = UserModel(username="test_user", email="test_user@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)  # Ensure `id` is populated

    post1 = ImagePostModel(image_url="http://example.com/image1.jpg", caption="First Post", user_id=user.id,
                           timestamp=datetime.now(timezone.utc))
    post2 = ImagePostModel(image_url="http://example.com/image2.jpg", caption="Second Post", user_id=user.id,
                           timestamp=datetime.now(timezone.utc))

    db_session.add_all([post1, post2])
    db_session.commit()

    response = client.put("/like_post", headers={"content-type": "application/json"}, json={"post_id": post2.id, "user_id": user.id})
    assert response.status_code == HTTPStatus.OK

    result = db_session.execute(text("SELECT post_id, user_id from likes;"))
    assert result.all() == [(post2.id, user.id)]