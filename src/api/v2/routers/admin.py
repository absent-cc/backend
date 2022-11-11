import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy.orm import Session
from src import utils
from src.api import accounts
from src.dataTypes import models, schemas, structs
from ....utils.prettifyTeacherName import prettifyName

from ....database import crud

router = APIRouter(prefix="/admin", tags=["Admin"])

# @router.get(
#     "/lookup/user/", response_model=List[schemas.UserInfoReturn], status_code=200
# )
# def getUserInfo(
#     first: str = None,
#     last: str = None,
#     creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
#     db: Session = Depends(accounts.getDBSession),  # Initializes a DB.
# ):
#     users: List[models.User]
#
#     if first == None and last == None:
#         users = crud.getAllUsers(db)
#     if first != None and last != None:
#         users = crud.getUsersByName(db, first, last)
#
#     returnList = []  # List that contains everything
#
#     for user in users:
#         rawSchedule: List[models.Class] = crud.getSchedule(
#             db, schemas.UserReturn(**user.__dict__)
#         )
#         settings: models.UserSettings = user.settings  # Grab settings
#         onboardedStatus = crud.checkOnboarded(db, uid=user.uid)
#
#         schedule = schemas.Schedule()
#
#         for entry in rawSchedule:
#             if getattr(schedule, str(entry.block)) == None:
#                 setattr(
#                     schedule,
#                     str(entry.block),
#                     [schemas.TeacherBase(**entry.teacher.__dict__)],
#                 )
#             else:
#                 setattr(
#                     schedule,
#                     str(entry.block),
#                     getattr(schedule, str(entry.block)).append(
#                         schemas.TeacherBase(**entry.teacher.__dict__)
#                     ),
#                 )
#
#         return_user = schemas.UserInfoReturn(  # Map info to userInto object
#             profile=schemas.UserReturn.from_orm(user),
#             schedule=schedule,
#             settings=schemas.UserSettings.from_orm(settings),
#             onboarded=onboardedStatus[0] and onboardedStatus[1],
#         )
#         returnList.append(return_user)
#
#     return returnList


@router.delete("/absences/", response_model=schemas.Bool, status_code=201)
def deleteAbsencesOnDay(
    date: Optional[datetime.date] = None,
    db: Session = Depends(accounts.getDBSession),
    creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
):
    if date is None:
        date = datetime.date.today()
    result = crud.removeAbsencesByDate(
        db, datetime.datetime(date.year, date.month, date.day)
    )
    return schemas.Bool(success=result)


@router.delete("/announcements/", response_model=schemas.Bool, status_code=201)
def deleteAnnouncementsByID(
    id: str,
    db: Session = Depends(accounts.getDBSession),
    creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
):
    result = crud.removeAnnouncement(db, schemas.AbsenceReturn(anid=id))
    return schemas.Bool(success=result)


@router.post("/announcements/", response_model=schemas.Bool, status_code=201)
def addAnnouncement(
    announcement: schemas.AnnouncementBase,
    db: Session = Depends(accounts.getDBSession),
    creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
):
    result = crud.addAnnouncement(db, announcement)
    return result


@router.put("/announcements/", response_model=schemas.Bool, status_code=201)
def updateAnnouncement(
    update: schemas.AnnouncementCreate,
    db: Session = Depends(accounts.getDBSession),
    creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
):
    result = crud.updateAnnouncement(
        db,
        schemas.AnnouncementUpdate(
            updateTime=datetime.datetime.now(), **update.__dict__
        ),
    )
    return result


@router.post("/schedule/", response_model=schemas.Bool, status_code=201)
def addSpecialDay(
    specialDay: schemas.SpecialDay,
    db: Session = Depends(accounts.getDBSession),
    creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
):
    # Check if a special day already exists
    try:
        schedule = structs.ScheduleWithTimes(specialDay.schedule)
        specialDay.schedule = schedule
    except:
        utils.raiseError(422, "Schedule data is wrong", structs.ErrorType.PAYLOAD)
        logger.error("Received incorrect format or invalid data for schedule")
        return schemas.Bool(success=False)
    result = crud.getSpecialDay(db, specialDay.date, specialDay.school)
    if result is None:
        logger.info(
            f"No special day found for date {specialDay.date}. Creating new one"
        )
        crud.addSpecialDay(db, specialDay)
    else:
        logger.info(
            f"Found special day for date {specialDay.date}. Updating entry with: {specialDay}"
        )
        crud.updateSpecialDay(db, specialDay)
    return schemas.Bool(success=True)


@router.delete("/schedule/", response_model=schemas.Bool, status_code=201)
def removeSpecialDay(
    date: datetime.date,
    school: Optional[structs.SchoolName] = None,
    db: Session = Depends(accounts.getDBSession),
    creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
):
    result = crud.removeSpecialDay(db, date, school)
    return schemas.Bool(success=True)


@router.get("/teacher/", response_model=schemas.TeacherReturn, status_code=201)
def getTeacher(
    first: Optional[str] = None,
    last: Optional[str] = None,
    school: Optional[structs.SchoolName] = None,
    db: Session = Depends(accounts.getDBSession),
    creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
):
    return crud.getTeacher(
        db, schemas.TeacherReturn(first=first, last=last, school=school)
    )


@router.get("/teacher/alias", response_model=Optional[schemas.TeacherAliasReturn], status_code=201)
def getTeacherAlias(
    first: str,
    last: str,
    school: structs.SchoolName,
    db: Session = Depends(accounts.getDBSession),
    # creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
):
    (first, last) = prettifyName(first, last)
    return crud.getTeacherAlias(db, schemas.TeacherAliasBase(first=first, last=last, school=school))


@router.post("/teacher/alias", response_model=schemas.Bool, status_code=201)
def addTeacherAlias(
    alias: schemas.TeacherAliasCreate,
    db: Session = Depends(accounts.getDBSession),
    # creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
):
    return crud.addTeacherAlias(db, alias)


@router.get("/teacher/aliases", response_model=List[schemas.TeacherAliasReturn], status_code=201)
def getTeacherAliases(
    db: Session = Depends(accounts.getDBSession),
    # creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
):
    return crud.getTeacherAliases(db)