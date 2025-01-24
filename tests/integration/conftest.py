from fastapi.testclient import TestClient
from pytest import fixture
from sqlalchemy.orm import Session

from src.app import app
from src.db.database import engine


@fixture
def client() -> TestClient:
    return TestClient(app)


@fixture
def make_migrations():
    pass
    # from alembic.config import Config
    # from alembic import command
    #
    # alembic_cfg = Config("alembic.ini")
    # command.upgrade(alembic_cfg, "head")
# @fixture
# def database_session():
#     connection = engine.connect()
#     transaction = connection.begin()
#     session = Session(bind=connection)  # TODO: Should this be AsyncSession?
#
#     yield session  # Run the test
#
#     session.close()
#     transaction.rollback()  # Undo changes
#     connection.close()
#
