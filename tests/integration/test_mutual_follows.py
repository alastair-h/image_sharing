from http import HTTPStatus

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user_model import UserModel


def test_get_mutual_followers_success(client, db_session: AsyncSession):
    user_1 = UserModel(username="user1", email="user1@example.com")
    user_2 = UserModel(username="user2", email="user2@example.com")
    mutual_follower_1 = UserModel(username="mutual1", email="mutual1@example.com")
    mutual_follower_2 = UserModel(username="mutual2", email="mutual2@example.com")
    non_mutual_follower_1 = UserModel(username="unrelated", email="unrelated@example.com")
    db_session.add_all([user_1, user_2, mutual_follower_1, mutual_follower_2, non_mutual_follower_1])
    db_session.commit()
    db_session.refresh(user_1)
    db_session.refresh(user_2)
    db_session.refresh(mutual_follower_1)
    db_session.refresh(mutual_follower_2)

    # Add follow relationships for mutual followers
    db_session.execute(
        text("INSERT INTO follows (follower, following) VALUES (:follower, :following)"),
        {"follower": mutual_follower_1.id, "following": user_1.id},
    )
    db_session.execute(
        text("INSERT INTO follows (follower, following) VALUES (:follower, :following)"),
        {"follower": mutual_follower_1.id, "following": user_2.id},
    )
    db_session.execute(
        text("INSERT INTO follows (follower, following) VALUES (:follower, :following)"),
        {"follower": mutual_follower_2.id, "following": user_1.id},
    )
    db_session.execute(
        text("INSERT INTO follows (follower, following) VALUES (:follower, :following)"),
        {"follower": mutual_follower_2.id, "following": user_2.id},
    )
    db_session.commit()

    response = client.get(f"/get_mutual_followers/{user_1.id}/{user_2.id}")

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert "mutual followers" in response_data
    mutual_followers_ids = response_data["mutual followers"]
    assert sorted(mutual_followers_ids) == [mutual_follower_1.id, mutual_follower_2.id]
