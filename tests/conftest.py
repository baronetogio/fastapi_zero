import factory
import factory.fuzzy
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from fast_zero.app import app
from fast_zero.db import get_session
from fast_zero.models import Todo, TodoState, User, reg
from fast_zero.security import get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}pwd')


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


@pytest.fixture()
def client(session):
    def test_session():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = test_session
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:
        _engine = create_engine(postgres.get_connection_url())

        with _engine.begin():
            yield _engine


@pytest.fixture()
def session(engine):
    reg.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    reg.metadata.drop_all(engine)


@pytest.fixture()
def user(session):
    user: User = UserFactory()
    clean_pwd = user.password
    user.password = get_password_hash(clean_pwd)

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_pwd = clean_pwd  # Monkey Patch

    return user


@pytest.fixture()
def user2(session):
    user: User = UserFactory()
    clean_pwd = user.password
    user.password = get_password_hash(clean_pwd)

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_pwd = clean_pwd  # Monkey Patch

    return user


@pytest.fixture()
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': user.clean_pwd},
    )
    return response.json()['access_token']
