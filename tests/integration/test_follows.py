from http import HTTPStatus

from sqlalchemy import text

from src.models.user_model import UserModel


def test_follow_user_success(client, db_session) -> None:
    # setup
    follower = UserModel(username="follower_user", email="follower@example.com")
    following = UserModel(username="following_user", email="following@example.com")
    db_session.add_all([follower, following])
    db_session.commit()
    db_session.refresh(follower)
    db_session.refresh(following)

    # Send a valid follow request
    response = client.put("/follow_user", headers={"content-type": "application/json"},
                          json={"follower_user_id": follower.id, "following_user_id": following.id})

    # Assert
    assert response.status_code == HTTPStatus.OK
    result = db_session.execute(text("SELECT follower, following FROM follows"))
    assert result.all() == [(follower.id, following.id)]


def test_follow_user_follower_not_found(client, db_session) -> None:
    # create only the user to be followed
    following = UserModel(username="following_user", email="following@example.com")
    db_session.add(following)
    db_session.commit()
    db_session.refresh(following)

    # attempt to follow with a non-existent follower
    response = client.put("/follow_user", headers={"content-type": "application/json"},
                          json={"follower_user_id": 999, "following_user_id": following.id})

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "Follower user not found"}


def test_follow_user_idempotency(client, db_session) -> None:
    follower = UserModel(username="follower_user", email="follower@example.com")
    following = UserModel(username="following_user", email="following@example.com")
    db_session.add_all([follower, following])
    db_session.commit()
    db_session.refresh(follower)
    db_session.refresh(following)

    response1 = client.put("/follow_user", headers={"content-type": "application/json"},
                           json={"follower_user_id": follower.id, "following_user_id": following.id})
    response2 = client.put("/follow_user", headers={"content-type": "application/json"},
                           json={"follower_user_id": follower.id, "following_user_id": following.id})

    assert response1.status_code == HTTPStatus.OK
    assert response2.status_code == HTTPStatus.OK

    result = db_session.execute(text("SELECT COUNT(*) FROM follows WHERE follower=:follower AND following=:following"),
                                {"follower": follower.id, "following": following.id})
    assert result.scalar() == 1


def test_get_following_list(client, db_session) -> None:
    # setup
    user1 = UserModel(username="user1", email="user1@example.com")
    user2 = UserModel(username="user2", email="user2@example.com")
    user3 = UserModel(username="user3", email="user3@example.com")
    db_session.add_all([user1, user2, user3])
    db_session.commit()
    db_session.refresh(user1)
    db_session.refresh(user2)
    db_session.refresh(user3)
    db_session.execute(text("INSERT INTO follows (follower, following) VALUES (:follower, :following)"),
                       {"follower": user1.id, "following": user2.id})  # user1 -> user2
    db_session.execute(text("INSERT INTO follows (follower, following) VALUES (:follower, :following)"),
                       {"follower": user3.id, "following": user1.id})  # user3 -> user1
    db_session.commit()

    # Act

    response = client.get(f"/get_following_list/{user1.id}")
    following = response.json()["following"]

    assert len(following) == 1
    assert following[0]["id"] == user2.id
    assert following[0]["username"] == "user2"

    # Assert: user1 is not following user3
    assert user3 not in following
