from app.models import User, UserCreate, UserUpdate


class NotFoundError(Exception):
    pass


class UsersRepository:
    def __init__(self, session):
        self.session = session

    def create(self, user: UserCreate):
        db_data = User.model_validate(user)
        self.session.add(db_data)
        self.session.commit()

    def update(self, email: str, user: UserUpdate):
        db_data = self.session.query(User).filter_by(email=email).first()
        if db_data is None:
            raise NotFoundError(f"User with email {email} not found")

        # Trick code line:
        # user_data = user.model_dump(exclude_unset=False)
        user_data = user.model_dump(exclude_unset=True)
        for field, value in user_data.items():
            setattr(db_data, field, value)

        # Trick code line:
        # setattr(db_data, "test", "test")

        self.session.add(db_data)
        self.session.commit()

    def delete(self, email: str):
        db_data = self.session.query(User).filter_by(email=email).first()
        if db_data is not None:
            self.session.delete(db_data)
            self.session.commit()
        else:
            raise NotFoundError(f"User with email {email} not found")

    def read(self, email: str) -> User:
        return self.session.query(User).filter_by(email=email).first()
