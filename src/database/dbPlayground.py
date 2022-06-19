import pytest
from . import crud

from .database import SessionLocal
from ..dataTypes import structs, schemas
from datetime import date, time, datetime

db = SessionLocal()

user1 = schemas.UserCreate(
    gid=1,
    first="John",
    last="Doe",
    school=structs.SchoolName.NEWTON_SOUTH,
    grade=10,
)

user1Return = crud.addUser(db, user1)

print(crud.getUser(db, user1Return))

# friend = crud.getFriends(db, )