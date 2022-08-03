from curses import can_change_color
import pytest
from . import crud

from .database import SessionLocal
from ..dataTypes import structs, schemas
from datetime import date, time, datetime

def run():
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

    session1 = schemas.SessionCreate(
        uid=model_user1.uid,
    )
    session2 = schemas.SessionCreate(
        uid=model_user2.uid,
    )
    session3 = schemas.SessionCreate(
        uid=model_user3.uid,
    )
    session4 = schemas.SessionCreate(
        uid=model_user4.uid,
    )

    model_session1 = crud.addSession(db, session1)
    model_session2 = crud.addSession(db, session2)
    model_session3 = crud.addSession(db, session3)
    model_session4 = crud.addSession(db, session4)

    token1 = schemas.Token(
        token="1"
    )
    token2 = schemas.Token(
        token="2"
    )
    token3 = schemas.Token(
        token="3"
    )
    token4 = schemas.Token(
        token="4"
    )

    crud.updateFCMToken(db, token1, model_session1.uid, model_session1.sid)
    crud.updateFCMToken(db, token2, model_session2.uid, model_session2.sid)
    crud.updateFCMToken(db, token3, model_session3.uid, model_session3.sid)
    crud.updateFCMToken(db, token4, model_session4.uid, model_session4.sid)

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

    settings1 = schemas.UserSettings(
        showFreeAsAbsent=True,
        notify=True,
        notifyWhenNone=True,
    )

    model_class1=crud.addClass(db, class1)
    model_class2 = crud.addClass(db, class2)
    model_class3 = crud.addClass(db, class3)
    model_class4 = crud.addClass(db, class4)

    model_settings1 = crud.updateUserSettings(db, settings1, model_user1.uid)
    model_settings2 = crud.updateUserSettings(db, settings1, model_user2.uid)
    model_settings3 = crud.updateUserSettings(db, settings1, model_user3.uid)
    model_settings4 = crud.updateUserSettings(db, settings1, model_user4.uid)
    
# canceled1 = schemas.Canceled(
#     date = date.today(),
#     cls = model_class1.construct_schema()
# )

# canceled2 = schemas.Canceled(
#     date = date.today(),
#     cls = model_class2.construct_schema()
# )

# canceled3 = schemas.Canceled(
#     date = date.today(),
#     cls = model_class3.construct_schema()
# )

# canceled4 = schemas.Canceled(
#     date = date.today(),
#     cls = model_class4.construct_schema()
# )


# model_canceled1 = crud.addCanceled(db, canceled1)
# model_canceled2 = crud.addCanceled(db, canceled2)
# model_canceled3 = crud.addCanceled(db, canceled3)
# model_canceled4 = crud.addCanceled(db, canceled4)

# print(crud.getCanceledsBySchool(db, structs.SchoolName.NEWTON_SOUTH, date.today()))
# list = crud.getClassesByTeacherAndBlock(db, model_teacher1.construct_schema(), structs.SchoolBlock.A)
# print(list)

# run()