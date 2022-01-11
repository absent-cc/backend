from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.openapi.utils import get_openapi
from dataStructs import *
from database.databaseHandler import DatabaseHandler
from api.accounts import Authenticator

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
auth = Authenticator()

def verifyCredentials(req: Request):
    try:
        clientID = req.headers["X-ClientID"]
        token = req.headers["X-Token"]
        valid = auth.validateToken(ClientID(clientID), Token(token))
    except KeyError:
        valid = False
    except ValueError:
        valid = False
    
    if not valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials."
        )
    return True

# /USERS ENDPOINTS

@absent.post("/users/login/", status_code=201,  response_model=SessionCredentials, tags=["users"])
async def authenticate(idToken: IDToken): #GOOGLE ID TOKEN WOULD BE ARG HERE.
    creds = auth.validateGoogleToken(idToken)
    print(creds)
    if creds != None:
        res = database.getStudentID(Student(None, creds['sub'], None, None, None, None))
        
        if res != None:
            session = auth.initializeSession(UUID(res))
            return SessionCredentials(studentUUID=str(session.studentUUID), clientID=str(session.clientID), token=str(session.token))
        else:
            name = creds['name'].split(' ', 1)
            student = Student(auth.generateUUID(), creds['sub'], name[0], name[1], None, None)
            database.addStudentToStudentDirectory(student)
            
            session = auth.initializeSession(student.uuid)
            return SessionCredentials(studentUUID=str(session.studentUUID), clientID=str(session.clientID), token=str(session.token))

    raise HTTPException(
        status_code=401,
        detail="Invalid credentials."
    )

@absent.put("/users/me/update", tags=["users"])
async def updateUserInfo(
userInfo: BasicInfo,
authorization: bool = Depends(verifyCredentials), 
X_ClientID: str | None = Header(None), 
X_Token: str | None = Header(None)
):
    uuid = X_ClientID.split('.')[1]
    student = Student(UUID(uuid), None, None, None, None, None)
    student = database.getStudent(student)
    usableUserInfo = dict(userInfo)

    if 'first' in usableUserInfo:
        student.first = usableUserInfo['first']
    if 'last' in usableUserInfo:
        student.last = usableUserInfo['last']
    if 'school' in usableUserInfo:
        try:
            student.school = SchoolNameMapper()[usableUserInfo['school']]
        except KeyError:
            student.school = None
    if 'grade' in usableUserInfo:
        student.grade = usableUserInfo['grade']

    if database.updateStudentInfo(student):
        return {"detail": "User information updated."}  
    else:
        return 422, {'detail': 'Database operation failed.'}  

@absent.get("/users/me/info", response_model=BasicInfo, tags=["users"])
async def returnUserInfo(
authorization: bool = Depends(verifyCredentials), 
X_ClientID: str | None = Header(None), 
X_Token: str | None = Header(None)
):
    uuid = X_ClientID.split('.')[1]
    student = Student(UUID(uuid), None, None, None, None, None)
    student = database.getStudent(student)
    schedule = database.getScheduleByStudent(student)

    return BasicInfo(uuid=uuid, subject=student.subject, first=student.first, last=student.last, school=ReverseSchoolNameMapper()[student.school], grade=student.grade, schedule=schedule)

