from fastapi import Depends, APIRouter
from api.helper import HelperFunctions
from dataStructs import *
from database.databaseHandler import DatabaseHandler
from api.accounts import Accounts 
from loguru import logger

router = APIRouter(prefix="/users", tags=["Users"])
accounts = Accounts()
database = DatabaseHandler()
helper = HelperFunctions()

@router.get("/me/info", response_model=BasicInfo)
async def returnUserInfo(
    creds: Session = Depends(accounts.verifyCredentials), 
):
    uuid = creds.cid.uuid
    student = Student(uid=uuid)
    student = database.getStudent(student)
    if student.school != None:
        schedule = database.getScheduleByStudent(student)
    else:
        return BasicInfo(profile=student)
    return BasicInfo(profile=student, schedule=schedule)

@router.put("/me/delete", status_code=201)
async def cancel(
    creds: Session = Depends(accounts.verifyCredentials)
):
    uuid = creds.cid.uuid
    student = Student(uid=uuid)
    if database.removeStudent(student):
        database.removeUserSessions(student)
        return helper.returnStatus("Account deleted.")
    helper.raiseError(500, "Operation failed.", ErrorType.DB)

@router.put("/me/update", status_code=201)
async def updateUserInfo(
    userInfo: BasicInfo,
    creds: Session = Depends(accounts.verifyCredentials), 
):
    uuid = creds.cid.uuid
    student = Student(uid=uuid)
    student = database.getStudent(student)

    profileSuccess = False
    scheduleSuccess = False

    if userInfo.profile != None:
        profileSuccess = accounts.updateProfile(student, userInfo.profile)
    else:
        profileSuccess = True

    if userInfo.schedule != None and student.school != None:
        scheduleSuccess = accounts.updateSchedule(student, userInfo.schedule)
    elif userInfo.schedule != None: 
        scheduleSuccess = False
    else: 
        scheduleSuccess = True

    if profileSuccess and scheduleSuccess:
        return helper.returnStatus("Information updated.")
    else:
        helper.raiseError(500, "Operation Failed", ErrorType.DB)