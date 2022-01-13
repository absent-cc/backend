from os import sched_get_priority_max
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api.helper import HelperFunctions
from dataStructs import *
from database.databaseHandler import DatabaseHandler
from api.accounts import Accounts

# All this fucking shit for the docs because I am legitimately this vain.

description = "The abSENT API powers the mobile app you love. Here, you can interact with it and implement it into your own applications if you so desire. All documentation is open; feel free to reach out to us for help if you're unsure about how something works."
tags_metadata = [
    {
        "name": "users",
        "description": "Endpoints for user-based operations. Session logic is also here.",
    },
    {
        "name": "admin",
        "description": "Endpoints for administration of the service, such as sending announcements and accessing private information. Unfortunately no one but us is cool enough to have access.",
    },

]

absent = FastAPI(
    title="abSENT",
    description=description,
    version="1.0.0",
    terms_of_service="https://absent.cc/terms",
    contact={
        "name": "abSENT",
        "url": "https://absent.cc",
        "email": "hello@absent.cc",
    },
    license_info={
        "name": "GNU Affero General Public License v3.0",
        "url": "https://www.gnu.org/licenses/agpl-3.0.html",
    },
    openapi_tags=tags_metadata
)

database = DatabaseHandler()
accounts = Accounts()
helper = HelperFunctions()

# /USERS ENDPOINTS

@absent.post("/users/login/", status_code=201,  response_model=SessionCredentials, tags=["users"])
async def authenticate(gToken: GToken): #GOOGLE ID TOKEN WOULD BE ARG HERE.
    creds = accounts.validateGoogleToken(gToken)
    print(creds)
    if creds != None:
        res = database.getStudentID(Student(gid=creds['sub']))
        if res != None:
            jwt = accounts.initializeSession(UUID(res))
            return SessionCredentials(token=jwt)
        else:
            return SessionCredentials(token=accounts.initializeSession(accounts.createAccount(creds)))

@absent.put("/users/me/update", tags=["users"], status_code=201)
async def updateUserInfo(
userInfo: BasicInfo,
creds: Session = Depends(accounts.verifyCredentials), 
):
    uuid = creds.cid.split('.')[1]
    student = Student(uid=UUID(uuid))
    student = database.getStudent(student)

    # if userInfo.profile != None:
    #     for key in userInfo.profile:
    #         if key == 'first' and userInfo.profile[key] != None:
    #             student.first = userInfo.profile[key]
    #         if key == 'last' and userInfo.profile[key] != None:
    #             student.last = userInfo.profile[key]
    #         if key == 'school' and userInfo.profile[key] != None:
    #             try:
    #                 student.school = SchoolNameMapper()[userInfo.profile[key]]
    #             except KeyError:
    #                 pass
    #         if key == 'grade' and userInfo.profile[key] != None:
    #             student.grade = userInfo.profile[key]

    profileSuccess = False
    scheduleSuccess = False

    if userInfo.profile != None:
        profileSuccess = accounts.updateProfile(student, userInfo.profile)
    else:
        profileSuccess = True

    if userInfo.schedule != None and student.school != None:
        scheduleSuccess = accounts.updateSchedule(student, userInfo.schedule)
    else: 
        scheduleSuccess = True

    if profileSuccess and scheduleSuccess:
        return helper.returnStatus("Information Updated")
    else:
        helper.raiseError(500, "Operation Failed", ErrorType.DB)

@absent.get("/users/me/info", response_model=BasicInfo, tags=["users"])
async def returnUserInfo(
creds: Session = Depends(accounts.verifyCredentials), 
):
    uuid = creds.cid.split('.')[1]
    student = Student(uid=UUID(uuid))
    student = database.getStudent(student)
    schedule = database.getScheduleByStudent(student)
    return BasicInfo(profile=student, schedule=schedule)

