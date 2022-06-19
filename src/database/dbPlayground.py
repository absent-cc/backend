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

user2 = schemas.UserCreate(
    gid=2,
    first="Jane",
    last="Doe",
    school=structs.SchoolName.NEWTON_SOUTH,
    grade=10,
)

user1Return = crud.addUser(db, user1)
user2Return = crud.addUser(db, user2)

print(crud.getUser(db, user1Return))
print(crud.getUser(db, user2Return))

friendship1 = schemas.FriendCreate(
    user = user1Return,
    friend = user2Return,
    status = structs.FriendshipStatus.ACQUAINTANCE,
    date = date.today(),
)

friendshipReturn1 = crud.addFriend(db, friendship1)
print(friendshipReturn1)

friend1 = schemas.FriendReturn(
    user = friendshipReturn1.user,
    friend = friendshipReturn1.friend,
    status = friendshipReturn1.status,
    date = friendshipReturn1.date,
)

print(friend1)
# friend = crud.getFriends(db, )