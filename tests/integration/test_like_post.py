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

    response = client.put("/like_post", headers={"content-type": "application/json"},
                          json={"post_id": post2.id, "user_id": user.id})
    assert response.status_code == HTTPStatus.OK

    result = db_session.execute(text("SELECT post_id, user_id from likes;"))
    assert result.all() == [(post2.id, user.id)]


def test_get_most_liked_posts(client, db_session) -> None:
    user = UserModel(username="test_user", email="test_user@example.com")
    user_2 = UserModel(username="test_user_2", email="test_user_2@example.com")
    db_session.add_all([user, user_2])
    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(user_2)

    post_1 = ImagePostModel(image_url="http://example.com/image1.jpg", caption="First Post", user_id=user.id,
                            timestamp=datetime.now(timezone.utc))
    post_2 = ImagePostModel(image_url="http://example.com/image2.jpg", caption="Second Post", user_id=user.id,
                            timestamp=datetime.now(timezone.utc))

    post_3 = ImagePostModel(image_url="http://example.com/image3.jpg", caption="Third Post", user_id=user_2.id,
                            timestamp=datetime.now(timezone.utc))
    post_4 = ImagePostModel(image_url="http://example.com/image4.jpg", caption="Fourth Post", user_id=user_2.id,
                            timestamp=datetime.now(timezone.utc))

    db_session.add_all([post_1, post_2, post_3, post_4])
    db_session.commit()

    # User 1 likes some post including his own
    db_session.execute(text("INSERT INTO likes (post_id, user_id) VALUES (:post_id, :user_id);"),
                       {"post_id": post_1.id, "user_id": user.id})

    db_session.execute(text("INSERT INTO likes (post_id, user_id) VALUES (:post_id, :user_id);"),
                       {"post_id": post_2.id, "user_id": user.id})

    db_session.execute(text("INSERT INTO likes (post_id, user_id) VALUES (:post_id, :user_id);"),
                          {"post_id": post_3.id, "user_id": user.id})

    # User 2 likes a post, post 2 is the most liked (2), post 1 and post 3 have 1 like, rest 0

    db_session.execute(text("INSERT INTO likes (post_id, user_id) VALUES (:post_id, :user_id);"),
                          {"post_id": post_2.id, "user_id": user_2.id})

    db_session.commit()

    response = client.get("/get_most_liked_posts")


    assert response.status_code == HTTPStatus.OK
    assert response.json()["most_liked_posts"][0] == 2
    assert response.json()["most_liked_posts"][1] in [1, 3]
    assert response.json()["most_liked_posts"][2] in [1, 3]
    assert 4 not in response.json()["most_liked_posts"]  # post 4 has no likes

