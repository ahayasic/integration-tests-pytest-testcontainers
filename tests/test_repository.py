from unittest.mock import Mock

from app.models import UserUpdate, User
from app.repository import UsersRepository


def test_update_user():
    # Arrange
    db_user = User(email="tony.stark@yahoo.com", full_name="Anthony Stark", occupation="CEO")
    mock_db_user = Mock(**db_user.model_dump())

    mock_session = Mock()
    mock_session.query().filter_by().first.return_value = mock_db_user

    user = UserUpdate(occupation="Mechanical Engineer")
    repository = UsersRepository(mock_session)

    # Act
    repository.update(db_user.email, user)

    # Assert
    mock_session.query.assert_called_with(User)
    mock_session.query().filter_by.assert_called_with(email=db_user.email)
    mock_session.query().filter_by().first.assert_called_once()
    mock_session.commit.assert_called_once()

    assert mock_db_user.email == db_user.email
    assert mock_db_user.occupation == user.occupation
    # Uncomment the line below to fix the test
    # assert mock_db_user.full_name == db_user.full_name
