from fastapi.testclient import TestClient
from pytest import fixture
from sqlalchemy.orm import Session

from src.app import app
from src.db.database import engine


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
