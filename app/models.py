from sqlmodel import Field, SQLModel
from typing import Optional


class UserBase(SQLModel):
    email: str = Field(primary_key=True, index=True)
    full_name: str
    occupation: str


class User(UserBase, table=True):
    pass


class UserCreate(UserBase):
    pass


class UserUpdate(SQLModel):
    full_name: Optional[str] = None
    occupation: Optional[str] = None
