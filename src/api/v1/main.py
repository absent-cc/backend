from fastapi import Depends, APIRouter
from api.v1.routers import users, admin
from dataTypes import structs, schemas, models
from sqlalchemy.orm import Session
from fuzzywuzzy import fuzz
import database.crud as crud
import api.utils as utils
import csv as c
import api.accounts as accounts


router = APIRouter(prefix="/v1")
router.include_router(users.router)

NNHS_FIRSTS = []
NNHS_LASTS = []

NSHS_FIRSTS = []
NSHS_LASTS = []

def readCSV(school: structs.SchoolName) -> bool:
    with open(f'data/{school}_teachers.csv') as f:
        csv = c.DictReader(f)
        print(f"{school}_FIRSTS")
        for col in csv:
            globals()[f"{school}_FIRSTS"].append(col['first'])
            globals()[f"{school}_LASTS"].append(col['last'])
    return True

readCSV(structs.SchoolName.NEWTON_NORTH)
readCSV(structs.SchoolName.NEWTON_SOUTH)

@router.get("/", status_code=200, tags=["Main"])
async def serviceInfo():
    return "This is the root page of the abSENT API, v1. Please call /login to get started."

@router.post("/login/", status_code=201, response_model=schemas.SessionCredentials, tags=["Main"])
async def authenticate(gToken: schemas.Token, db: Session = Depends(accounts.getDBSession)): # GToken is expected in request body.
    creds = accounts.validateGoogleToken(gToken) # Accounts code is used to validate the Google JWT, returns all the data from it.
    if creds != None:
        res = crud.getUser(db, schemas.UserReturn(gid=creds['sub'])) # SUB = GID, this is used as our external identifier. This code checks if the user is in the DB.
        if res != None: 
            # Session is created, both tokens issued. Returned to user in body.
            session = crud.addSession(db, schemas.SessionCreate(uid=res.uid))
            token = accounts.generateToken(f"{session.sid}.{res.uid}")
            refresh = accounts.generateRefreshToken(f"{session.sid}.{res.uid}") 
            return schemas.SessionCredentials(token=token, refresh=refresh)
        else: 
            # Account is created with the information we have from Google.
            name = creds['name'].split(' ', 1)
            if len(name) == 2:
                user = schemas.UserCreate(gid=int(creds['sub']), first=name[0], last=name[1])
            else:
                user = schemas.UserCreate(gid=int(creds['sub']), first=name[0])
            user = crud.addUser(db, user)
            id = user.uid 
            # Session is created, both tokens issued. Returned to user in body.
            session = crud.addSession(db, schemas.SessionCreate(uid=res.uid))
            token = accounts.generateToken(f"{session.sid}.{res.uid}")
            refresh = accounts.generateRefreshToken(f"{session.sid}.{res.uid}")
            return schemas.SessionCredentials(token=token, refresh=refresh)
            
# Endpoint used to request new main token using refresh token. Refresh token is expected in authentication header, with Bearer scheme.
@router.post("/refresh/", status_code=201, response_model=schemas.SessionCredentials, tags=["Main"])
async def refresh(cid = Depends(accounts.verifyRefreshToken)): # Here, the refresh token is decoded and verified using our accounts code.
    if cid != None: # This is the actual validity check here.
        token = accounts.generateToken(cid) # Issue a new token, using accounts code. Since these tokens are stateless no DB interaction is needed.
        return schemas.SessionCredentials(token=token) # Return this using our credentials schema.
    else:
        utils.raiseError(401, "Invalid refresh token provided", structs.ErrorType.AUTH) # Otherwise, raise an error of type AUTH, signifying an invalid token.

@router.post("/autocomplete/", status_code=201, response_model=schemas.AutoComplete, tags=["Main"])
async def autocomplete(partialName: schemas.PartialName):
    if len(partialName.name) > 2:
        matches = []
        for index in range(len(globals()[f"{partialName.school}_FIRSTS"])):
            str = globals()[f"{partialName.school}_FIRSTS"][index] + " " + globals()[f"{partialName.school}_LASTS"][index]
            ratio = fuzz.partial_ratio(partialName.name.lower(), str.lower())
            if ratio > 80:
                matches.append(str)
        return schemas.AutoComplete(suggestions=matches)
    return None