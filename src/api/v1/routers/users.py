from fastapi import Depends, APIRouter
from api.helper import HelperFunctions
from dataTypes import structs, schemas
from database.crud import CRUD
from api.accounts import Accounts 
from loguru import logger

router = APIRouter(prefix="/users", tags=["Users"])
accounts = Accounts()
helper = HelperFunctions()

@router.get("/me/info", response_model=schemas.UserReturn) # Info endpoint.
async def returnUserInfo(
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials), # Authentication.
    db: CRUD = Depends(accounts.getDBSession) # Initializes a DB.
):
    user = schemas.UserReturn(uid=creds.uid) # Creates husk user.
    user = db.getUser(user) # Gets the rest of the info.
    userReturn = schemas.UserReturn.from_orm(user) # Builds a Pydantic model from this Alchemy model.
    userReturn.schedule = schemas.Schedule.scheduleFromList(user.schedule) # Converts list-schedule into Schedule object.

    return userReturn # Returns user.

@router.put("/me/delete", status_code=201) # Cancellation endpoint.
async def cancel(
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials), # Authentication.
    db: CRUD = Depends(accounts.getDBSession) # Initializes a DB.
):
    user = schemas.UserReturn(uid=creds.uid) # Creates husk user.
    if db.removeUser(user): # Attemps remove.
        return helper.returnStatus("Account deleted.") # Sends sucess.
    helper.raiseError(500, "Operation failed.", structs.ErrorType.DB) # Else, errors.

@router.put("/me/update", status_code=201) # Update endpoint, main.
async def updateUserInfo(
    user: schemas.UserInfo, # Takes a user object: this is the NEW info, not the current info.
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials), # Authentication.
    db: CRUD = Depends(accounts.getDBSession) # Initializes a DB.
):

    db.updateProfile(user.profile, creds.uid) # Updates the profile info (everything save the schedule). 
    db.updateSchedule(schemas.UserReturn(uid=creds.uid, school=user.profile.school), user.schedule) # Updates the schedule.

    return helper.returnStatus("Information updated.") # Returns success.

@router.put("/me/update/profile", status_code=201) # Update endpoint, profile.
async def updateUserInfo(
    profile: schemas.UserBase, # Takes just profile information.
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials), # Authentication.
    db: CRUD = Depends(accounts.getDBSession) # Initializes a DB.
):

    db.updateProfile(profile, creds.uid) # Updates the profile info.

    return helper.returnStatus("Information updated.") # Returns success.

@router.put("/me/update/schedule", status_code=201) # Update endpoint, schedule.
async def updateUserInfo(
    schedule: schemas.Schedule, # Takes just a schedule.
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials), # Authentication.
    db: CRUD = Depends(accounts.getDBSession) # Initializes a DB.
):
    user = schemas.UserReturn(uid=creds.uid) # Creates husk user. 

    db.updateSchedule(user, schedule) # Updates schedule.

    return helper.returnStatus("Information updated.") # Returns success.