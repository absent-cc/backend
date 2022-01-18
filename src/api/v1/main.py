from fastapi import Depends, APIRouter
from api.helper import HelperFunctions
from api.accounts import Accounts
from .routers import users, admin
from dataStructs import *
from loguru import logger
from database import models, schemas
from database.crud import CRUD

# All this fucking shit for the docs because I am legitimately this vain.

accounts = Accounts()
helper = HelperFunctions()
router = APIRouter(prefix="/v1")
database = CRUD()
router.include_router(users.router)
#absent.include_router(admin.router)

@router.get("/", status_code=200, tags=["Main"])
async def serviceInfo():
    return "This is the root page of the abSENT API, v1. Please call /login to get started."

@router.post("/login/", status_code=201, response_model=schemas.SessionCredentials, tags=["Main"])
async def authenticate(gToken: schemas.GToken): #GOOGLE ID TOKEN WOULD BE ARG HERE.
    creds = accounts.validateGoogleToken(gToken)
    if creds != None:
        res = database.getUser(schemas.UserReturn(gid=creds['sub']))
        if res != None:
            details = accounts.initializeSession(res.uid)
            refresh = accounts.generateRefreshToken(details[1])
            return schemas.SessionCredentials(token=details[0], refresh=refresh)
        else:
            id = accounts.createAccount(creds)
            if id != None:
                details = accounts.initializeSession(id)
                refresh = accounts.generateRefreshToken(id)
                return schemas.SessionCredentials(token=details[0], refresh=refresh)
            else:
                helper.raiseError(500, "Account creation failed", ErrorType.DB)

@router.post("/refresh/", status_code=201, response_model=schemas.SessionCredentials, tags=["Main"])
async def refresh(cid = Depends(accounts.verifyRefreshToken)):
    if cid != None:
        token = accounts.generateToken(cid)
        return schemas.SessionCredentials(token=token)
    else:
        helper.raiseError(401, "Invalid refresh token provided", ErrorType.AUTH)



