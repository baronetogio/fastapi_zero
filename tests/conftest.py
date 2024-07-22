import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.db import get_session
from fast_zero.models import User, reg


@pytest.fixture()
def client(session):
    def test_session():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = test_session
        yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    reg.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    reg.metadata.drop_all(engine)


@pytest.fixture()
def user(session):
    user = User(
        username='testeusername', email='test@test.com', password='password'
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return user
