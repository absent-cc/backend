from curses import can_change_color
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
    last="Diane",
    school=structs.SchoolName.NEWTON_NORTH,
    grade=10,
)

user4 = schemas.UserCreate(
    gid=4,
    first="Jill",
    last="Diane",
    school=structs.SchoolName.NEWTON_NORTH,
    grade=10,
)

teacher1 = schemas.TeacherCreate(
    first="Rachel",
    last="Becker",
    school=structs.SchoolName.NEWTON_SOUTH,
)

teacher2 = schemas.TeacherCreate(
    first="Amy",
    last="Winston",
    school=structs.SchoolName.NEWTON_NORTH,
)

model_user1 = crud.addUser(db, user1)
model_user2 = crud.addUser(db, user2)
model_user3 = crud.addUser(db, user3)
model_user4 = crud.addUser(db, user4)

model_teacher1 = crud.addTeacher(db, teacher1)
model_teacher2 = crud.addTeacher(db, teacher2)
# model_teacher1 = crud.getTeacherByName(db, "Rachel", "Becker")

class1 = schemas.Class(
    tid = model_teacher1.tid,
    block = structs.SchoolBlock.C,
    uid = model_user1.uid,
)

class2 = schemas.Class(
    tid = model_teacher1.tid,
    block = structs.SchoolBlock.C,
    uid = model_user2.uid
)

class3 = schemas.Class(
    tid = model_teacher2.tid,
    block = structs.SchoolBlock.C,
    uid = model_user3.uid
)

class4 = schemas.Class(
    tid = model_teacher2.tid,
    block = structs.SchoolBlock.C,
    uid = model_user4.uid
)

model_class1=crud.addClass(db, class1)
model_class2 = crud.addClass(db, class2)
model_class3 = crud.addClass(db, class3)
model_class4 = crud.addClass(db, class4)

canceled1 = schemas.Canceled(
    date = date.today(),
    cls = model_class1.construct_schema()
)

canceled2 = schemas.Canceled(
    date = date.today(),
    cls = model_class2.construct_schema()
)

canceled3 = schemas.Canceled(
    date = date.today(),
    cls = model_class3.construct_schema()
)

canceled4 = schemas.Canceled(
    date = date.today(),
    cls = model_class4.construct_schema()
)


# model_canceled1 = crud.addCanceled(db, canceled1)
# model_canceled2 = crud.addCanceled(db, canceled2)
# model_canceled3 = crud.addCanceled(db, canceled3)
# model_canceled4 = crud.addCanceled(db, canceled4)

# print(crud.getCanceledsBySchool(db, structs.SchoolName.NEWTON_SOUTH, date.today()))
# list = crud.getClassesByTeacherAndBlock(db, model_teacher1.construct_schema(), structs.SchoolBlock.A)
# print(list)