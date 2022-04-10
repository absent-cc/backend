import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api import accounts
from src.dataTypes import models, schemas
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

# @router.get("/lookup/teachers/", response_model=schemas.TeachersInfoReturn, status_code=200):
# def getTeachersInfo(
#     creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),

# if __name__ == "__main__":
#     print("Admin router")
#     _db = SessionLocal()
#     specialDay: List[structs.SchoolBlock] = [structs.SchoolBlock.A, structs.SchoolBlock.B, structs.SchoolBlock.C]

#     crud.addSpecialDay(_db, datetime.date(2020, 1, 1), specialDay)
#     print(crud.getSpecialDay(_db, datetime.date(2020, 1, 1)))