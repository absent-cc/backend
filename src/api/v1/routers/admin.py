import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api import accounts
from src.dataTypes import models, schemas
from ....database import crud

router = APIRouter(prefix="/admin", tags=["Admin"])

# Query by name
# Delete absences
# Put in new absences


@router.get("/lookup/user/", response_model=schemas.UsersInfoReturn, status_code=200)
def getUserInfo(
    first: str = None,
    last: str = None,
    creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
    db: Session = Depends(accounts.getDBSession),  # Initializes a DB.
):
    if first is None and last is None:
        users: List[models.User] = crud.getAllUsers(db)
    if first is not None and last is not None:
        users: List[models.User] = crud.getUsersByName(db, first, last)

    returnList = []  # List that contains everything

    for user in users:
        schedule: List[models.Class] = user.schedule  # Grab schedule
        settings: models.UserSettings = user.settings[0]  # Grab settings
        onboardedStatus = crud.checkOnboarded(db, uid=user.uid)

        user = schemas.UserInfoReturn(  # Map info to userInto object
            profile=schemas.UserReturn.from_orm(user),
            schedule=schemas.Schedule.from_orm(schedule),
            settings=schemas.UserSettings.from_orm(settings),
            onboarded=onboardedStatus[0] and onboardedStatus[1],
        )
        returnList.append(user)

    return schemas.UsersInfoReturn(users=returnList)


@router.delete("/absences/delete/", response_model=schemas.Bool, status_code=200)
def deleteAbsencesOnDay(
    date: datetime.date = None,
    db: Session = Depends(accounts.getDBSession),
    creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),
):
    if date is None:
        date = datetime.date.today()
    result = crud.removeAbsencesByDate(db, datetime(date.year, date.month, date.day))
    return schemas.Bool(success=result)


# @router.get("/lookup/teachers/", response_model=schemas.TeachersInfoReturn, status_code=200):
# def getTeachersInfo(
#     creds: schemas.SessionReturn = Depends(accounts.verifyAdmin),

# if __name__ == "__main__":
#     print("Admin router")
#     _db = SessionLocal()
#     specialDay: List[structs.SchoolBlock] = [structs.SchoolBlock.A, structs.SchoolBlock.B, structs.SchoolBlock.C]

#     crud.addSpecialDay(_db, datetime.date(2020, 1, 1), specialDay)
#     print(crud.getSpecialDay(_db, datetime.date(2020, 1, 1)))