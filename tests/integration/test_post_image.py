from http import HTTPStatus

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://image_sharing_user:image_sharing_password@db:5432/image_sharing_db"  # TODO: Move to a config file or pyantic settings


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:

    engine = create_async_engine(DATABASE_URL)
    Session = sessionmaker(engine, class_=AsyncSession)

    async with Session() as session:
        async with session.begin():
            yield session
            q = text("TRUNCATE TABLE images RESTART IDENTITY CASCADE;")
            await session.execute(q)
            await session.commit()


@pytest.mark.asyncio
async def test_post_image(client, db_session) -> None:
    image_post_data = {"image_url": "https://www.example.com/image.jpg", "caption": "A caption"}
    response = client.post(
        "/create_post",
        headers={"content-type": "application/json"},
        json=image_post_data
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == image_post_data

    result = await db_session.execute(
        text("SELECT image_url, caption FROM images"))
    assert result.rowcount == 1
    inserted_item = result.fetchone()

    assert inserted_item is not None
    assert inserted_item.image_url == image_post_data["image_url"]
    assert inserted_item.caption == image_post_data["caption"]
