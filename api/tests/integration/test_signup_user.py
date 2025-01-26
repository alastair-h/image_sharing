from http import HTTPStatus

from sqlalchemy import text


def test_sign_up_new_user(client, db_session) -> None:

    user_data = {"username": "test_user", "email": "testuser@example.org"}
    response = client.post(
        "/signup_user",
        headers={"content-type": "application/json"},
        json=user_data,
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["username"] == user_data["username"]
    assert response.json()["email"] == user_data["email"]

    result = db_session.execute(text("SELECT email, username FROM users"))
    inserted_item = result.fetchone()
    assert inserted_item is not None
    assert inserted_item.email == user_data["email"]
    assert inserted_item.username == user_data["username"]
