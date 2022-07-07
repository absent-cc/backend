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

user3 = schemas.UserCreate(
    gid=3,
    first="Jack",
    last="Black",
    school=structs.SchoolName.NEWTON_SOUTH,
    grade=10,
)


user1Return = crud.addUser(db, user1)
user2Return = crud.addUser(db, user2)
user3Return = crud.addUser(db, user3)

print(crud.getUser(db, user1Return))
print(crud.getUser(db, user2Return))
print(crud.getUser(db, user3Return).construct_schema())

user3Schema = crud.getUser(db, user3Return).construct_schema()
print(user3Schema)
print("HERE")
print(type(user3Schema))

print(user3Schema.schedule)
print(type(user3Schema.schedule))

friendship1 = schemas.FriendCreate(
    user = user1Return,
    friend = user2Return,
    status = structs.FriendshipStatus.ACQUAINTANCE,
    date = date.today(),
)

friendship2 = schemas.FriendCreate(
    user = user1Return,
    friend = user3Return,
    status = structs.FriendshipStatus.BFF,
    date = date.today(),
)

friendshipReturn1 = crud.addFriend(db, friendship1)
friendshipReturn2 = crud.addFriend(db, friendship2)

friend1 = schemas.FriendReturn(
    user = friendshipReturn1.user,
    friend = friendshipReturn1.friend,
    status = friendshipReturn1.status,
    date = friendshipReturn1.date,
)

# friend2 = friendshipReturn2.construct_schema()

# crud.removeFriend(db, friendshipReturn1)
print(f"Before change: {crud.getFriend(db, friendshipReturn2)}")

friendshipReturn3 = schemas.FriendReturn(
    user = friendshipReturn2.user,
    friend = friendshipReturn2.friend,
    status = structs.FriendshipStatus.NONE,
    date = date.today(),
)

updated = crud.updateFriendStatus(db, friendshipReturn3, structs.FriendshipStatus.BLOCKED)
print(updated)
# print(structs.FriendshipStatus.NONE > structs.FriendshipStatus.ACQUAINTANCE)
# friend = crud.getFriends(db, )