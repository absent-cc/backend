from typing_extensions import Required
from fastapi import FastAPI, HTTPException, Depends, Request, Header
from dataStructs import *
from database.databaseHandler import DatabaseHandler
from api.accounts import Authenticator

absent = FastAPI()
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

@absent.post("/login/", status_code=201,  response_model=SessionCredentials)
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

@absent.put("/users/me/update")
async def updateUserInfo(
userInfo: BasicInfo,
authorization: bool = Depends(verifyCredentials), 
X_ClientID: str | None = Header(None), 
X_Token: str | None = Header(None)
):
    uuid = X_ClientID.split('.')[1]
    student = Student(UUID(uuid), None, None, None, None, None)
    student = database.getStudent(student)

    return {"detail": "User information updated."}    

@absent.get("/users/me/info", response_model=BasicInfo)
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

