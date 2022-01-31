from fastapi import Depends, APIRouter
from dataTypes import structs, schemas
from loguru import logger
from sqlalchemy.orm import Session
import database.crud as crud
import api.utils as utils
import api.accounts as accounts

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me/info", response_model=schemas.UserReturn, status_code=200) # Info endpoint.
async def returnUserInfo(
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials), # Authentication.
    db: Session = Depends(accounts.getDBSession) # Initializes a DB.
):
    user = schemas.UserReturn(uid=creds.uid) # Creates husk user.
    user = crud.getUser(db, user) # Gets the rest of the info.
    userReturn = schemas.UserReturn.from_orm(user) # Builds a Pydantic model from this Alchemy model.
    userReturn.schedule = schemas.Schedule.scheduleFromList(user.schedule) # Converts list-schedule into Schedule object.

    return userReturn # Returns user.

@router.get("/me/sessions", response_model=schemas.SessionList, status_code=200)
async def getSessionList(
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials),
    db: Session = Depends(accounts.getDBSession)
):
    sessions = crud.getSessionList(db, schemas.UserReturn(uid=creds.uid))
    return schemas.SessionList(sessions=sessions)

@router.put("/me/delete", status_code=201) # Cancellation endpoint.
async def cancel(
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials), # Authentication.
    db: Session = Depends(accounts.getDBSession) # Initializes a DB.
):
    user = schemas.UserReturn(uid=creds.uid) # Creates husk user.
    if crud.removeUser(db, user): # Attemps remove.
        return utils.returnStatus("Account deleted.") # Sends sucess.
    utils.raiseError(500, "Operation failed", structs.ErrorType.DB) # Else, errors.

@router.put("/me/update", status_code=201) # Update endpoint, main.
async def updateUserInfo(
    user: schemas.UserInfo, # Takes a user object: this is the NEW info, not the current info.
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials), # Authentication.
    db: Session = Depends(accounts.getDBSession) # Initializes a DB.
):

    profile = crud.updateProfile(db, user.profile, creds.uid) # Updates the profile info (everything save the schedule). 
    schedule = crud.updateSchedule(db, schemas.UserReturn(uid=creds.uid, school=user.profile.school), user.schedule) # Updates the schedule.
    token = crud.updateFCMToken(db, user.fcm, creds.uid, creds.sid)

    if (profile, token) != None and schedule:
        return utils.returnStatus("Information updated") # Returns success.
    else:
        utils.raiseError(500, "Operation failed", structs.ErrorType.DB)

@router.put("/me/update/profile", status_code=201) # Update endpoint, profile.
async def updateUserInfo(
    profile: schemas.UserBase, # Takes just profile information.
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials), # Authentication.
    db: Session = Depends(accounts.getDBSession) # Initializes a DB.
):

    result = crud.updateProfile(db, profile, creds.uid) # Updates the profile info.

    if result != None:
        return utils.returnStatus("Information updated") # Returns success.
    else:
        utils.raiseError(500, "Operation failed", structs.ErrorType.DB)

@router.put("/me/update/schedule", status_code=201) # Update endpoint, schedule.
async def updateUserInfo(
    schedule: schemas.Schedule, # Takes just a schedule.
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials), # Authentication.
    db: Session = Depends(accounts.getDBSession) # Initializes a DB.
):
    user = schemas.UserReturn(uid=creds.uid) # Creates husk user. 

    result = crud.updateSchedule(db, user, schedule) # Updates schedule.
    
    if result:
        return utils.returnStatus("Information updated") # Returns success.
    else:
        utils.raiseError(500, "Operation failed", structs.ErrorType.DB)

@router.put("/me/update/fcm", status_code=201)
async def updateFirebaseToken(
    token: schemas.Token,
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials),
    db: Session = Depends(accounts.getDBSession)
):
    result = crud.updateFCMToken(db, token, creds.uid, creds.sid)

    if result != None:
        return utils.returnStatus("Information updated") # Returns success.
    else:
        utils.raiseError(500, "Operation failed", structs.ErrorType.DB)

@router.put("/me/sessions/revoke", status_code=201)
async def revokeSession(
    session: schemas.SessionReturn,
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials),
    db: Session = Depends(accounts.getDBSession)
):
    session.uid = creds.uid
    if crud.removeSession(db, session):
        return utils.returnStatus("Session revoked")
    else:
        utils.raiseError(500, "Session deletion failed", structs.ErrorType.DB)

