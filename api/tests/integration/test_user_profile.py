from http import HTTPStatus

from sqlalchemy import text

from src.models.user_model import UserModel


def test_get_user_profile_success(client, db_session):
    user = UserModel(username="test_user", email="test_user@example.com")
    user_2 = UserModel(username="test_user_2", email="test_user_2@example.com")
    user_3 = UserModel(username="test_user_3", email="test_user_3@example.com")
    db_session.add_all([user, user_2, user_3])
    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(user_2)
    db_session.refresh(user_3)

    db_session.execute(
        text("INSERT INTO follows (follower, following) VALUES (:follower, :following)"),
        {"follower": 2, "following": user.id},
    )
    db_session.execute(
        text("INSERT INTO follows (follower, following) VALUES (:follower, :following)"),
        {"follower": user.id, "following": 3},
    )
    db_session.commit()

    response = client.get(f"/user_profile?user_id={user.id}")

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data["user"]["username"] == "test_user"
    assert response_data["following_count"] == 1  # Test user follows 1 person
    assert response_data["follower_count"] == 1  # Test user has 1 follower
