from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
from pydantic.errors import NoneIsAllowedError
from dataStructs import *
from database.databaseHandler import DatabaseHandler
from api.accounts import Authenticator

app = FastAPI()
database = DatabaseHandler()
auth = Authenticator()

def verifyToken(req: Request):
    token = req.headers["Authorization"]
    try:
        isValid = auth.validateToken(Token(token), req.path_params['uuid'])
    except ValueError:
        isValid = False
    if not isValid:
        raise HTTPException(
            status_code=401,
            detail="Invalid token."
        )
    return True

@app.get("/")
async def root():
    return {"message": "Hello World"}

# /USERS ENDPOINTS

class IDToken(BaseModel):
    idToken: str

    def __str__(self):
        return self.idToken

@app.post("/login/idtoken")
async def authenticate(IDToken: IDToken): #GOOGLE ID TOKEN WOULD BE ARG HERE.
    if auth.validateGoogleToken(IDToken):
        res = database.getStudentID(Student(None, "your mom lmfao", None, None, None, None))
        if res != None:
            auth.initializeSession(UUID(res))
        return True
    return False

@app.get("/users/{uuid}/schedule")
async def returnSchedule(uuid: str, authorized: bool = Depends(verifyToken)):
    if authorized:
        return database.getScheduleByStudent(Student(UUID(uuid), None, None, None, None, None))


