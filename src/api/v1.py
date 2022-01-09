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
    return (clientID, token)

# /USERS ENDPOINTS

@absent.post("/login/")
async def authenticate(idToken: IDToken): #GOOGLE ID TOKEN WOULD BE ARG HERE.
    print(idToken)
    if auth.validateGoogleToken(idToken):
        res = database.getStudentID(Student(None, "TestSubject", None, None, None, None))
        print(res)
        if res != None:
            session = auth.initializeSession(UUID(res))
            return {'UUID': str(session.studentUUID), 'ClientID': str(session.clientID), 'Token': str(session.token)}
        else:
            pass
            # Create account chain here.

    raise HTTPException(
        status_code=401,
        detail="Invalid credentials."
    )

@absent.get("/users/me/info")
async def returnUserInfo(credentials: tuple[ClientID, Token] = Depends(verifyCredentials)):
    uuid = database.getUUIDFromCreds(credentials[0], credentials[1])
    student = Student(UUID(uuid), None, None, None, None, None)
    student = database.getStudent(student)
    schedule = database.getScheduleByStudent(student)

    return BasicInfo(uuid=uuid, subject=student.subject, first=student.first, last=student.last, school=ReverseSchoolNameMapper()[student.school], grade=student.grade, schedule=schedule)
