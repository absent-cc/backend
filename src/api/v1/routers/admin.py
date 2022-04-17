import datetime
from multiprocessing.context import SpawnContext
from typing import List, Optional

from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy.orm import Session
from src import utils
from src.api import accounts
from src.dataTypes import models, schemas, structs

from ....database import crud

router = APIRouter(prefix="/admin", tags=["Admin"])


# Query by name
# Delete absences
# Put in new absences


@router.get("/lookup/user/", response_model=List[schemas.UserInfoReturn], status_code=200)
def getUserInfo(
    first: str = None,
    last: str = None,
    # creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
    db: Session = Depends(accounts.getDBSession),  # Initializes a DB.
):  
    users: List[models.User]

    if first == None and last == None:
        users = crud.getAllUsers(db)
    if first != None and last != None:
        users = crud.getUsersByName(db, first, last)

    returnList = []  # List that contains everything

    for user in users:
        rawSchedule: List[models.Class] = crud.getSchedule(db, schemas.UserReturn(**user.__dict__))
        settings: models.UserSettings = user.settings  # Grab settings
        onboardedStatus = crud.checkOnboarded(db, uid=user.uid)

        schedule = schemas.Schedule()

        for entry in rawSchedule:
            if getattr(schedule, str(entry.block)) == None:
                setattr(schedule, str(entry.block), [schemas.TeacherBase(**entry.teacher.__dict__)])
            else:
                setattr(schedule, str(entry.block), getattr(schedule, str(entry.block)).append(schemas.TeacherBase(**entry.teacher.__dict__)))

        print(schedule)

        return_user = schemas.UserInfoReturn(  # Map info to userInto object
            profile=schemas.UserReturn.from_orm(user),
            schedule=schedule,
            settings=schemas.UserSettings.from_orm(settings),
            onboarded=onboardedStatus[0] and onboardedStatus[1],
        )
        returnList.append(return_user)
    
    return returnList


@router.delete("/absences/delete/", response_model=schemas.Bool, status_code=200)
def deleteAbsencesOnDay(
    date: Optional[datetime.date] = None,
    db: Session = Depends(accounts.getDBSession),
    creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
):
    if date is None:
        date = datetime.date.today()
    result = crud.removeAbsencesByDate(db, datetime.datetime(date.year, date.month, date.day))
    return schemas.Bool(success=result)

@router.delete("/announcements/delete/", response_model=schemas.Bool, status_code=200)
def deleteAnnouncementsByID(
    id: str,
    db: Session = Depends(accounts.getDBSession),
    creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
):
    result = crud.removeAnnouncement(db, schemas.AbsenceReturn(anid=id))
    return schemas.Bool(success=result)

@router.post("/announcements/add/", response_model=schemas.Bool, status_code=200)
def addAnnouncement(
    announcement: schemas.AnnouncementBase,
    db: Session = Depends(accounts.getDBSession),
    creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
):
    result = crud.addAnnouncement(db, announcement)
    return result

@router.post("/announcements/update/", response_model=schemas.Bool, status_code=200)
def updateAnnouncement(
    update: schemas.AnnouncementCreate,
    db: Session = Depends(accounts.getDBSession),
    creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
):
    result = crud.updateAnnouncement(db, schemas.AnnouncementUpdate(updateTime=datetime.datetime.now(), **update.__dict__))
    return result

# @router.post("/schedule/add/", response_model=schemas.Bool, status_code=200)
# def addSpecialDay(
#     date: datetime.date,
#     name: str,
#     schedule: structs.ScheduleWithTimes,
#     note: str = None,

#     db: Session = Depends(accounts.getDBSession),
#     creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
#     ):
#     result = crud.addSpecialDay(db, date, name, schedule, note)
#     return result

@router.post("/schedule/update/", response_model=schemas.Bool, status_code=200)
def updateSpecialDay(
    specialDay: schemas.SpecialDay,
    db: Session = Depends(accounts.getDBSession),
    # creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
):
    # Check if a special day already exists
    try:
        schedule = structs.ScheduleWithTimes(specialDay.schedule)
        specialDay.schedule = schedule
    except:
        utils.raiseError(422, "Schedule data is wrong", structs.ErrorType.PAYLOAD)
        logger.error("Received incorrect format or invalid data for schedule")
        return schemas.Bool(success=False)
    result = crud.getSpecialDay(db, specialDay.date)
    if result is None:
        logger.info(f"No special day found for date {specialDay.date}. Creating new one")
        crud.addSpecialDay(db, specialDay)
    else:
        logger.info(f"Found special day for date {specialDay.date}. Updating entry with: {specialDay}")
        crud.updateSpecialDay(db, specialDay)
    return schemas.Bool(success=True)
