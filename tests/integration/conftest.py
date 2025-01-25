import pytest
from fastapi.testclient import TestClient
from pytest import fixture
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from src.app import app


@fixture
def client() -> TestClient:
    return TestClient(app)


@fixture
def make_migrations():  # TODO: integrate creation of migrations into setup
    pass
    # from alembic.config import Config
    # from alembic import command
    #
    # alembic_cfg = Config("alembic.ini")
    # command.upgrade(alembic_cfg, "head")


DATABASE_URL = "postgresql+psycopg2://image_sharing_user:image_sharing_password@db:5432/image_sharing_db"

# Shared engine and session for synchronous tests
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(engine)


@pytest.fixture
def db_session():
    with Session() as session:
        # Clean up the database before each test
        session.execute(text("TRUNCATE TABLE image_posts RESTART IDENTITY CASCADE;"))
        session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
        session.execute(text("TRUNCATE TABLE follows RESTART IDENTITY CASCADE;"))
        session.execute(text("TRUNCATE TABLE likes RESTART IDENTITY CASCADE;"))
        session.commit()

        yield session
        # Optionally clean up the database after each test
        session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
        session.execute(text("TRUNCATE TABLE image_posts RESTART IDENTITY CASCADE;"))
        session.execute(text("TRUNCATE TABLE follows RESTART IDENTITY CASCADE;"))
        session.execute(text("TRUNCATE TABLE likes RESTART IDENTITY CASCADE;"))
        session.commit()
