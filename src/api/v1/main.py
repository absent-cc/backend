from fastapi import Depends, APIRouter
from .routers import teachers, users, analytics, badges, admin
from ...dataTypes import structs, models, schemas
from sqlalchemy.orm import Session
from fuzzywuzzy import fuzz
from ...database import crud
from ...api import utils
from ...api import accounts


router = APIRouter(prefix="/v1")
router.include_router(users.router)
router.include_router(teachers.router)
router.include_router(analytics.router)
router.include_router(badges.router)
router.include_router(admin.router)

@router.get("/", status_code=200, tags=["Main"])
async def serviceInfo():
    return "This is the root page of the abSENT API, v1. Please call /login to get started."

@router.post("/login/", status_code=201, response_model=schemas.SessionCredentials, tags=["Main"])
def authenticate(gToken: schemas.Token, db: Session = Depends(accounts.getDBSession)): # GToken is expected in request body.
    creds = accounts.validateGoogleToken(gToken) # Accounts code is used to validate the Google JWT, returns all the data from it.
    if creds != None:
        onboardStatus = crud.checkOnboarded(db, gid=creds["sub"]) # Check if the user has been onboarded.
        if onboardStatus[0] == True: 
            # User is in our table
            # Return  return the session credentials and if they have been completly onboarded.
            res = crud.getUser(db, schemas.UserReturn(gid=creds["sub"]))
            # Session is created, both tokens issued. Returned to user in body.
            session = crud.addSession(db, schemas.SessionCreate(uid=res.uid))
            token = accounts.generateToken(f"{session.sid}.{res.uid}")
            refresh = accounts.generateRefreshToken(f"{session.sid}.{res.uid}") 
            return schemas.SessionCredentials(token=token, refresh=refresh, onboarded=onboardStatus[1])
            
            # Remember that onboardStatus[1] is the status of whether or not they have any classes in our system. Read the checkOnboarded function for more info (database/crud.py)
        else:
            # User is not in table
            # Return session credentials and if they have been completly onboarded.
            # Account is created with the information we have from Google.
            name = creds['name'].split(' ', 1)
            if len(name) == 2:
                user = schemas.UserCreate(gid=int(creds['sub']), first=name[0], last=name[1])
            else:
                user = schemas.UserCreate(gid=int(creds['sub']), first=name[0])
            
            user = crud.addUser(db, user)
            # Session is created, both tokens issued. Returned to user in body.
            session = crud.addSession(db, schemas.SessionCreate(uid=user.uid))
            token = accounts.generateToken(f"{session.sid}.{user.uid}")
            refresh = accounts.generateRefreshToken(f"{session.sid}.{user.uid}")
            return schemas.SessionCredentials(token=token, refresh=refresh, onboarded=False)
            # User could not have been onboarded if they were not even in our user table.
            
# Endpoint used to request new main token using refresh token. Refresh token is expected in authentication header, with Bearer scheme.
@router.post("/refresh/", status_code=201, response_model=schemas.SessionCredentials, tags=["Main"])
def refresh(cid = Depends(accounts.verifyRefreshToken)): # Here, the refresh token is decoded and verified using our accounts code.
    if cid != None: # This is the actual validity check here.
        token = accounts.generateToken(cid) # Issue a new token, using accounts code. Since these tokens are stateless no DB interaction is needed.
        db, = accounts.getDBSession()
        sid, uid = cid.split(".") # Split the cid into the session id and user id.
        inSystem, hasClasses = crud.checkOnboarded(db, uid=uid) # Check if the user has been onboarded.
        return schemas.SessionCredentials(token=token, onboarded=(inSystem and hasClasses), refresh=cid) # Return this using our credentials schema.
    else:
        utils.raiseError(401, "Invalid refresh token provided", structs.ErrorType.AUTH) # Otherwise, raise an error of type AUTH, signifying an invalid token.

@router.put("/logout/", status_code=201, tags=["Main"])
def logout(creds: schemas.SessionReturn = Depends(accounts.verifyCredentials), db: Session = Depends(accounts.getDBSession)):
    return crud.removeSession(db, creds)