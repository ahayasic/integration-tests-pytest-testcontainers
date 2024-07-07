import sqlalchemy
import sqlmodel

from app.repository import UsersRepository
from app.models import UserCreate, UserUpdate, User

import pytest
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session", name="postgres")
def postgres_fixture():
    with PostgresContainer("postgres:16.2-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session", name="engine")
def engine_fixture(postgres):
    engine = sqlalchemy.create_engine(postgres.get_connection_url())
    return engine


# Don't confuse the 'session' fixture
# with the session scope of pytest fixtures
@pytest.fixture(name="session")
def session_fixture(engine):
    sqlmodel.SQLModel.metadata.create_all(engine)
    with sqlalchemy.orm.Session(engine) as session:
        yield session
    sqlmodel.SQLModel.metadata.drop_all(engine)


def read_user(session, email: str) -> User:
    return session.query(User).filter_by(email=email).first()


def create_user(session, user: UserCreate):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()


def test_update_user(session):
    # Arrange
    db_user = UserCreate(email="tony.stark@yahoo.com", full_name="Anthony Stark", occupation="CEO")
    create_user(session, db_user)

    user = UserUpdate(occupation="Mechanical Engineer")
    repository = UsersRepository(session)

    # Act
    repository.update(db_user.email, user)

    # Assert
    expected_user = User(email=db_user.email, full_name=db_user.full_name, occupation=user.occupation)  # type: ignore
    result_user = read_user(session, db_user.email)
    assert result_user == expected_user
