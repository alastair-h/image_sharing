import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from http import HTTPStatus
from src.app import app

@pytest.yield_fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

DATABASE_URL = "postgresql+psycopg2://image_sharing_user:image_sharing_password@db:5432/image_sharing_db"

# Shared engine and session for synchronous tests
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(engine)

@pytest.fixture
def db_session():
    with Session() as session:
        # Clean up the database before each test
        session.execute(text("TRUNCATE TABLE images RESTART IDENTITY CASCADE;"))
        session.commit()
        yield session
        # Optionally clean up the database after each test
        session.execute(text("TRUNCATE TABLE images RESTART IDENTITY CASCADE;"))
        session.commit()


# client = TestClient(app)
# client_2 = TestClient(app)

def test_post_image(client, db_session) -> None:
    # with Session() as session:


    image_post_data = {"image_url": "https://www.example.com/image.jpg", "caption": "A caption"}
    response = client.post(
        "/create_post",
        headers={"content-type": "application/json"},
        json=image_post_data,
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == image_post_data

    # Query the database to verify the item was inserted
    result = db_session.execute(text("SELECT image_url, caption FROM images"))
    inserted_item = result.fetchone()

    assert inserted_item is not None
    assert inserted_item.image_url == image_post_data["image_url"]
    assert inserted_item.caption == image_post_data["caption"]

def test_post_image_2(client, db_session) -> None:

    image_post_data = {"image_url": "https://www.example.com/second-image.jpg", "caption": "Another caption"}
    response = client.post(
        "/create_post",
        headers={"content-type": "application/json"},
        json=image_post_data,
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == image_post_data

    # Query the database to verify the item was inserted
    result = db_session.execute(text("SELECT image_url, caption FROM images"))
    inserted_item = result.fetchone()

    assert inserted_item is not None
    assert inserted_item.image_url == image_post_data["image_url"]
    assert inserted_item.caption == image_post_data["caption"]
