import pytest
from . import crud

from .database import SessionLocal
from ..dataTypes import structs, schemas
from datetime import date, time, datetime

db = SessionLocal()

# test = schemas.AnnouncementCreate(
#     anid = "1",
#     title="Test Announcement",
#     content="This is a test announcement.",
#     date=date.today(),
#     school=structs.SchoolName.NEWTON_SOUTH
# )

# crud.addAnnouncement(db, test)
# entry = crud.getAnnouncementByID(db, "1")
# print(entry)
# update = schemas.AnnouncementUpdate(
#     anid="1",
#     title="UPDATED",
#     content="CONTENT UDPATED",
#     school = structs.SchoolName.NEWTON_NORTH,
#     updateTime=datetime.now()
# )
# crud.updateAnnouncement(db, update)
# entry = crud.getAnnouncementByID(db, "1")
# print(entry)

# crud.getAnnouncements(db, top=2, bottom=0)

# crud.removeAnnouncement(db, entry)
# entry = crud.getAnnouncementByID(db, "1")

# crud.addSpecialDay(db, schemas.SpecialDay(
#     name="Test Day",
#     date=date.today(),
#     school=structs.SchoolName.NEWTON_SOUTH,
#     schedule = structs.ScheduleWithTimes(),
#     note = "This is a test day."
# ))

# print(crud.getSpecialDay(db, date.today()))

# crud.updateSpecialDay(db, schemas.SpecialDay(
#     name="Updating",
#     date=date.today(),
#     school=structs.SchoolName.NEWTON_SOUTH,
#     schedule = structs.ScheduleWithTimes(
#         [
#             structs.BlockWithTimes(
#                 block=structs.SchoolBlock.A,
#                 startTime=time(9, 0),
#                 endTime=time(10, 0),
#             )
#         ]
#         )
#     )
# )

# joe = schemas.SpecialDay(
#     name="Updating",
#     date=date.today(),
#     school=structs.SchoolName.NEWTON_SOUTH,
#     schedule = structs.ScheduleWithTimes(
#         [
#             structs.BlockWithTimes(
#                 block=structs.SchoolBlock.A,
#                 startTime=time(9, 0),
#                 endTime=time(10, 0),
#             )
#         ]
#         )
#     )

returnTeach = crud.addTeacher(db, schemas.TeacherCreate(
    first = "Kevin",
    last = "Yang",
    school = structs.SchoolName.NEWTON_SOUTH,
    ))

aliasCreation = crud.addTeacherAlias(db, schemas.TeacherAliasCreate(
                    first="Kev",
                    last="Yang",
                    tid = returnTeach.tid
                    )
                )

# print(aliasCreation)

absence = schemas.AbsenceCreate(
    teacher = schemas.TeacherCreate(
        first = "kEv",
        last = "yang",
        school = structs.SchoolName.NEWTON_SOUTH,
    ),
    date = date.today(),
)

crud.addAbsence(db, absence)