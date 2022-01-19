from fastapi import Depends, APIRouter
from api.helper import HelperFunctions
from dataTypes import structs, schemas
from database.crud import CRUD
from api.accounts import Accounts 
from loguru import logger

router = APIRouter(prefix="/users", tags=["Users"])
accounts = Accounts()
helper = HelperFunctions()
database = CRUD()

@router.get("/me/info", response_model=schemas.UserReturn)
async def returnUserInfo(
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials), 
):
    uid = creds.uid
    user = schemas.UserReturn(uid=uid)
    user = database.getUser(user)
    userReturn = schemas.UserReturn.from_orm(user)
    userReturn.schedule = schemas.Schedule.scheduleFromList(user.schedule)

    return userReturn

@router.put("/me/delete", status_code=201)
async def cancel(
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials)
):
    uid = creds.uid
    user = schemas.UserReturn(uid=uid)
    if database.removeUser(user):
        return helper.returnStatus("Account deleted.")
    helper.raiseError(500, "Operation failed.", structs.ErrorType.DB)

@router.put("/me/update", status_code=201)
async def updateUserInfo(
    user: schemas.UserInfo,
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials), 
):

    database.updateProfile(user.profile, creds.uid)
    database.updateSchedule(schemas.UserReturn(uid=creds.uid, school=user.profile.school), user.schedule)

    return helper.returnStatus("Information updated.")

@router.put("/me/update/profile", status_code=201)
async def updateUserInfo(
    profile: schemas.UserBase,
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials), 
):

    database.updateProfile(profile, creds.uid)

    return helper.returnStatus("Information updated.")

@router.put("/me/update/schedule", status_code=201)
async def updateUserInfo(
    schedule: schemas.Schedule,
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials), 
):
    uid = creds.uid
    user = schemas.UserReturn(uid=uid)
    user = database.getUser(user)

    database.updateSchedule(user, schedule)

    return helper.returnStatus("Information updated.")