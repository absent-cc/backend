from fastapi import FastAPI, HTTPException, Depends, Request
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
        valid = auth.validateToken(clientID, Token(token))
    except KeyError:
        valid = False
    except ValueError:
        valid = False
    
    if not valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials."
        )
    return token

# /USERS ENDPOINTS

@absent.post("/login/")
async def authenticate(IDToken: IDToken): #GOOGLE ID TOKEN WOULD BE ARG HERE.
    if auth.validateGoogleToken(IDToken):
        res = database.getStudentID(Student(None, "TestSubject", None, None, None, None))
        print(res)
        if res != None:
            session = auth.initializeSession(UUID(res))
            return {'UUID': str(session.uuid), 'ClientID': str(session.clientID), 'Token': str(session.token)}
        else:
            pass
            # Create account chain here.

    raise HTTPException(
        status_code=401,
        detail="Invalid credentials."
    )

@absent.get("/users/{uuid}/info")
async def returnUserInfo(uuid: str, credentials: tuple[str, Token] = Depends(verifyCredentials)):
    student = Student(UUID(uuid), None, None, None, None, None)
    student = database.getStudent(student)
    schedule = database.getScheduleByStudent(student)

    return {
        'UUID': str(student.uuid),
        'Subject': str(student.subject),
        'First': str(student.first),
        'Last': str(student.last),
        'School': ReverseSchoolNameMapper()[student.school],
        'Grade': student.grade,
        'Schedule': schedule
    }

