from datetime import timezone, datetime
from http import HTTPStatus

from sqlalchemy import text

from src.models.image_model import ImagePostModel
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


# def test_follow_user_follower_not_found(client, db_session) -> None:
#     # setup:  create only the user to be followed
#     following = UserModel(username="following_user", email="following@example.com")
#     db_session.add(following)
#     db_session.commit()
#     db_session.refresh(following)
#
#     # attempt to follow with a non-existent follower
#     response = client.put("/follow_user", headers={"content-type": "application/json"},
#                           json={"follower_user_id": 999, "following_user_id": following.id})  # Non-existent follower ID
#
#     # Assert the response is 404
#     assert response.status_code == HTTPStatus.NOT_FOUND
#     assert response.json() == {"detail": "Follower user not found"}
