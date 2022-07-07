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

teacher1 = schemas.TeacherCreate(
    first="Jack",
    last="Black",
    school=structs.SchoolName.NEWTON_SOUTH,
)

model_user1 = crud.addUser(db, user1)
model_teacher1 = crud.addTeacher(db, teacher1)

class1 = schemas.Class(
    tid = model_teacher1.tid,
    block = structs.SchoolBlock.A,
    uid = model_user1.uid,
)

model_class1=crud.addClass(db, class1)

canceled1 = schemas.Canceled(
    date = date.today(),
    cls = model_class1.construct_schema()
)
    
model_canceled = crud.addCanceled(db, canceled1)


