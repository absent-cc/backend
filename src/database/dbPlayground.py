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

# returnTeach = crud.addTeacher(db, schemas.TeacherCreate(
#     first = "Tuen Wing",
#     last = "Fan",
#     school = structs.SchoolName.NEWTON_SOUTH,
#     ))

# aliasCreation = crud.addTeacherAlias(db, schemas.TeacherAliasCreate(
#                     first="Tuen",
#                     last="Wing Fan",
#                     tid = returnTeach.tid
#                     )
#                 )

# # print(aliasCreation)

# absence = schemas.AbsenceCreate(
#     teacher = schemas.TeacherCreate(
#         first = "Tuen",
#         last = "Wing Fan",
#         school = structs.SchoolName.NEWTON_SOUTH,
#     ),
#     date = date.today(),
# )

# crud.addAbsence(db, absence)

# specialDay1 = schemas.SpecialDay(
#     name="Test Day",
#     date=date.today(),
#     school=structs.SchoolName.NEWTON_SOUTH,
#     schedule=structs.SchoolBlocksOnDayWithTimes()[1],
#     note="This is a test day.",
# )

# crud.addSpecialDay(db, specialDay1)

# print(crud.getSpecialDay(db, date.today(), specialDay1.school))

# crud.updateSpecialDay(
#     db,
#     schemas.SpecialDay(
#         name="New Entry",
#         date=date.today(),
#         school=structs.SchoolName.NEWTON_SOUTH,
#         schedule=structs.SchoolBlocksOnDayWithTimes()[1],
#         note="This is a test day.",
#     ),
# )


# print(crud.getSpecialDay(db, date.today(), specialDay1.school).name)

brianBaron = schemas.TeacherCreate(
    first="Bob",
    last="Baron",
    school=structs.SchoolName.NEWTON_SOUTH,
)

crud.addTeacher(db, brianBaron)

print(crud.getTeacher(db, teacher=schemas.TeacherReturn(first="Brian", last="Baron", school=structs.SchoolName.NEWTON_SOUTH)))
# Alias Creation
alias1 = schemas.TeacherAliasCreate(
    first="Brian",
    last="Baron",
    school=structs.SchoolName.NEWTON_SOUTH,
    actual_first="Bob",
    actual_last="Baron",
    actual_school=structs.SchoolName.NEWTON_SOUTH,
)

returnAlias = crud.addTeacherAlias(db, alias1)
print(crud.getTeacherAlias(db, alias1))

print(crud.getTeacherAliases(db))

# crud.updateTeacherAlias(db, schemas.TeacherAliasUpdate(entryToUpdate=returnAlias, first="Bible", last="Baron", school=structs.SchoolName.NEWTON_SOUTH))