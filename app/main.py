from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, Session, create_engine

from app.models import UserCreate, UserUpdate
from app.repository import UsersRepository, NotFoundError


engine = create_engine("sqlite:///db.sqlite")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_repository():
    with Session(engine) as session:
        yield UsersRepository(session)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    print("Shutting down")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Users API"}


@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, repository: UsersRepository = Depends(get_repository)):
    try:
        repository.create(user)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")


@app.put("/users/{email}", status_code=status.HTTP_200_OK)
def update_user(email: str, user: UserUpdate, repository: UsersRepository = Depends(get_repository)):
    try:
        repository.update(email, user)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.delete("/users/{email}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(email: str, repository: UsersRepository = Depends(get_repository)):
    try:
        repository.delete(email)
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.get("/users/{email}")
def read_user(email: str, repository: UsersRepository = Depends(get_repository)):
    user = repository.read(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
