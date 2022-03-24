
import configparser
import datetime
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.api import accounts
from src.dataTypes import models, schemas, structs

from ....api import utils
from ....database import crud
from ....database.database import SessionLocal

router = APIRouter(prefix="/admin", tags=["Admin"])

def adminAuth(creds: schemas.SessionReturn):
    config = configparser.ConfigParser()
    config.read('config.ini'    )
    admin_uids = config['ADMIN']['uids']
    
    if creds.uid in admin_uids:
        return True
    return False

# Query by name
# Delete absences
# Put in new absences

@router.get("/lookup/", response_model=schemas.UsersInfoReturn, status_code=200)
def getUserInfo(
    first: str = None,
    last: str = None,
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials),
    db: Session = Depends(accounts.getDBSession), # Initializes a DB.
):
    if adminAuth(creds):
        if first == None and last == None:
            users: List[models.User] = crud.getAllUsers(db)
        if first != None and last != None:
            users: List[models.User] = crud.getUsersByName(db, first, last)

        returnList = [] # List that contains everything

        for user in users:
            schedule: models.Class = crud.getClassesByUser(db, schemas.UserReturn(uid=user.uid)) # Grab schedule
            settings: models.UserSettings = crud.getUserSettings(db, schemas.UserReturn(uid=user.uid)) # Grab settings
            onboardedStatus = crud.checkOnboarded(db, uid=user.uid)

            user = schemas.UserInfoReturn( # Map info to userInto object
                profile=schemas.UserReturn.from_orm(user),
                schedule=schemas.Schedule.from_orm(schedule),
                settings=schemas.UserSettings.from_orm(settings),
                onboarded= onboardedStatus[0] and onboardedStatus[1]
            )
            returnList.append(user)

        return schemas.UsersInfoReturn(users=returnList)
    return utils.raiseError(401, "Unauthorized. None admin privileges", structs.ErrorType.AUTH)

@router.delete("/absences/delete/", response_model=schemas.Bool, status_code = 200)
def deleteAbsencesOnDay(
    date: datetime.date = None,
    db: Session = Depends(accounts.getDBSession),
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials)
):
    if adminAuth(creds):
        if date == None:
            date = datetime.date.today()
        result = crud.removeAbsencesByDate(db, datetime(date.year, date.month, date.day))
        return schemas.Bool(success=result)
    return utils.raiseError(401, "Unauthorized. None admin privileges", structs.ErrorType.AUTH)

# @router.put("absences/manual/", response_model=schemas.ManualAbsencesReturn, status_code=200)
# def manualAbsencesPut(
#     db: Session = Depends(accounts.getDBSession),
#     creds: schemas.SessionReturn = Depends(accounts.verifyCredentials)
    
# )

if __name__ == "__main__":
    print("Admin router")
    _db = SessionLocal()
    specialDay: List[structs.SchoolBlock] = [structs.SchoolBlock.A, structs.SchoolBlock.B, structs.SchoolBlock.C]

    crud.addSpecialDay(_db, datetime.date(2020, 1, 1), specialDay)
    print(crud.getSpecialDay(_db, datetime.date(2020, 1, 1)))
