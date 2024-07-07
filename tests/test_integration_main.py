import sqlalchemy
import pytest

from app.main import app, get_repository
from app.repository import User, UserCreate, UsersRepository

from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session", name="postgres")
def postgres_fixture():
    with PostgresContainer("postgres:16.2-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session", name="engine")
def engine_fixture(postgres):
    engine = sqlalchemy.create_engine(postgres.get_connection_url())
    return engine


# Don't confuse the session fixture
# with the session scope of pytest fixtures
@pytest.fixture(name="session")
def session_fixture(engine):
    SQLModel.metadata.create_all(engine)
    with sqlalchemy.orm.Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session):
    def get_repository_override():
        return UsersRepository(session)

    app.dependency_overrides[get_repository] = get_repository_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def read_user(session, email: str) -> User:
    return session.query(User).filter_by(email=email).first()


def create_user(session, user: UserCreate):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()


def test_update_user(client, session):
    # Arrange
    db_user = UserCreate(
        email="tony.stark@yahoo.com", full_name="Anthony Stark", occupation="CEO"
    )
    create_user(session, db_user)

    payload = {"occupation": "Mechanical Engineer"}

    # Act
    response = client.put(f"/users/{db_user.email}", json=payload)

    # Assert
    result_user = read_user(session, db_user.email)

    assert response.status_code == 200
    assert result_user.occupation == payload["occupation"]
    assert result_user.full_name == db_user.full_name
    assert result_user.email == db_user.email
