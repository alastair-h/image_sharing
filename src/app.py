import http
from http import HTTPStatus

from fastapi import FastAPI, Response, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.models.image import Image

app = FastAPI()
DATABASE_URL = "postgresql+asyncpg://image_sharing_user:image_sharing_password@db:5432/image_sharing_db"

engine = create_async_engine(DATABASE_URL)
Session = sessionmaker(engine, class_=AsyncSession)


async def get_db_session() -> AsyncSession:
    async with Session() as session:
        async with session.begin():
            yield session


class ImagePost(BaseModel):
    image_url: str
    caption: str = Field(..., max_length=100)


@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}


@app.post("/create_post", status_code=HTTPStatus.OK, responses={
    HTTPStatus.OK: {"description": "OK - Post processed successfully"},
    HTTPStatus.CREATED: {"description": "Created - Post successfully created"},
}, )
async def image_post(image: ImagePost,
                     response: Response,
                     db: AsyncSession = Depends(get_db_session)) -> ImagePost:
    new_image = Image(image_url=image.image_url, caption=image.caption)
    db.add(new_image)
    await db.commit()
    response.status_code = http.HTTPStatus.CREATED
    return image
