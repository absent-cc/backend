from fastapi import Depends, APIRouter
from api.helper import HelperFunctions
from api.accounts import Accounts
from api.v1.routers import users, admin
from dataTypes import structs, schemas, models
from database.crud import CRUD


accounts = Accounts()
helper = HelperFunctions()
router = APIRouter(prefix="/v1")
router.include_router(users.router)
#absent.include_router(admin.router)

@router.get("/", status_code=200, tags=["Main"])
async def serviceInfo():
    return "This is the root page of the abSENT API, v1. Please call /login to get started."

@router.post("/login/", status_code=201, response_model=schemas.SessionCredentials, tags=["Main"])
async def authenticate(gToken: schemas.GToken, db: CRUD = Depends(helper.getDBSession)): # GToken is expected in request body.
    creds = accounts.validateGoogleToken(gToken) # Accounts code is used to validate the Google JWT, returns all the data from it.
    if creds != None:
        res = db.getUser(schemas.UserReturn(gid=creds['sub'])) # SUB = GID, this is used as our external identifier. This code checks if the user is in the DB.
        if res != None: 
            # Session is created, both tokens issued. Returned to user in body.
            details = accounts.initializeSession(res.uid) 
            refresh = accounts.generateRefreshToken(details[1]) 
            return schemas.SessionCredentials(token=details[0], refresh=refresh)
        else:
            id = accounts.createAccount(creds) # Account is created with the information we have from Google.
            if id != None:
                # Session is created, both tokens issued. Returned to user in body.
                details = accounts.initializeSession(id)
                refresh = accounts.generateRefreshToken(id)
                return schemas.SessionCredentials(token=details[0], refresh=refresh)
            else:
                helper.raiseError(500, "Account creation failed", structs.ErrorType.DB)

# Endpoint used to request new main token using refresh token. Refresh token is expected in authentication header, with Bearer scheme.
@router.post("/refresh/", status_code=201, response_model=schemas.SessionCredentials, tags=["Main"])
async def refresh(cid = Depends(accounts.verifyRefreshToken)): # Here, the refresh token is decoded and verified using our accounts code.
    if cid != None: # This is the actual validity check here.
        token = accounts.generateToken(cid) # Issue a new token, using accounts code. Since these tokens are stateless no DB interaction is needed.
        return schemas.SessionCredentials(token=token) # Return this using our credentials schema.
    else:
        helper.raiseError(401, "Invalid refresh token provided", structs.ErrorType.AUTH) # Otherwise, raise an error of type AUTH, signifying an invalid token.