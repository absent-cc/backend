import jwt
import time
from ..api import utils
from ..database import crud
from ..dataTypes import schemas, structs
from google.auth.transport import requests
from google.oauth2 import id_token
from cryptography.hazmat.primitives import serialization
from fastapi import Depends, Security, FastAPI
from loguru import logger
from ..database.database import SessionLocal
from fastapi.security.api_key import APIKeyHeader, APIKey
import configparser

API_KEY_NAME = "absent-auth"
credsHeader = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def getDBSession():
    # Dependency
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

with open('creds/id_rsa.pub', 'r') as f:
    PUB_KEY = f.read()
with open('creds/id_rsa', 'r') as f:
    PRIV_KEY = f.read()

def verifyCredentials(
        creds: str = Security(credsHeader),
        db = Depends(getDBSession)
    ) -> schemas.SessionReturn:

    creds = decodeToken(creds)
    if creds == None:
        return None
    sub = creds['sub'].split('.')
    session = schemas.SessionReturn(uid=sub[1], sid=sub[0])
    session = crud.getSession(db, session)
    if session != None:
        return session
    logger.info(f"Credential check failed: {sub}")
    utils.raiseError(401, "Invalid credentials", structs.ErrorType.AUTH)

def verifyRefreshToken(creds: str = Security(credsHeader)) -> str:
    cid = validateRefreshToken(creds)
    return cid

#
# Token validation.
#

# Google IDToken check.
def validateGoogleToken(token) -> dict:

    # Various Client IDs for Backend + App frontend
    BACKEND_ID = "349911558418-9d07ptkk7pg7aqq58qkj5tshi8bq9s5v.apps.googleusercontent.com"
    EXPO_ID = "349911558418-rusr95n8ttq00iujmk3je4q5fmkiib5t.apps.googleusercontent.com"
    IOS_ID = "349911558418-9tm5hh1jgk7k7obhcor3k9l3l2ejt3ue.apps.googleusercontent.com"
    ANDROID_ID = "349911558418-mjtpkjiuqfd5lcihfdi2kni73ja13ou5.apps.googleusercontent.com"
    DEV_ANDROID_ID = "349911558418-t8ld1clvadk0jg04rn3q86hms34h9js0.apps.googleusercontent.com"
    DEV_IOS_ID = "349911558418-6ps5ft9k690fva0ouc7popfbtr1s0l6a.apps.googleusercontent.com"

    CLIENT_IDs = [
        BACKEND_ID,
        EXPO_ID,
        IOS_ID,
        ANDROID_ID,
        DEV_IOS_ID,
        DEV_ANDROID_ID
    ]

    NEWTON = "newton.k12.ma.us"
    ABSENT = "absent.cc"

    try:
        idInfo = id_token.verify_token(token.token, requests.Request(), audience=CLIENT_IDs)
        logger.info(f"Sucessful Google login: {idInfo['sub']}")
    except BaseException as error:
        logger.info(f"Invalid Google token POSTed.")
        utils.raiseError(401, error, structs.ErrorType.AUTH)
    try:
        domain = idInfo['email'].split("@")[1]
        verified = idInfo['email_verified']
        if domain != NEWTON and domain != ABSENT and not verified:
            logger.info(f"Google token for a non-NPS account POSTed")
            utils.raiseError(401, "Not an NPS issued account", structs.ErrorType.AUTH)
    except BaseException:
        logger.info(f"Google token for a non-NPS account POSTed")
        utils.raiseError(401, "Not an NPS issued account", structs.ErrorType.AUTH)
    return idInfo

def validateRefreshToken(jwt: str) -> str:
    creds = decodeRefreshToken(jwt)
    try:
        if creds['ref'] == True:
            return creds['sub']
        else:
            return None
    except:
        return None

# Building block for our token check.
def decodeToken(webtoken: str) -> dict:
    key = serialization.load_ssh_public_key(PUB_KEY.encode())
    try:
        decoded = jwt.decode(
            webtoken,
            key=key,
            options={"require": ["iss", "exp", "sub", "iat"]},
            algorithms=['RS256',]
            )
    except BaseException as error:
        utils.raiseError(401, error, structs.ErrorType.AUTH)
    return decoded

# Building block for our token check.
def decodeRefreshToken(webtoken: str) -> dict:
    key = serialization.load_ssh_public_key(PUB_KEY.encode())
    try:
        decoded = jwt.decode(
            webtoken,
            key=key,
            options={"require": ["iss", "sub", "iat", "ref"]},
            algorithms=['RS256',]
            )
    except BaseException as error:
        utils.raiseError(401, error, structs.ErrorType.AUTH)
    return decoded

#
# Various functions for generating secrets and IDs.
#

# Takes a ClientID and generates signed JWT for authentication purposes.
def generateToken(clientID: str) -> str:
    EXP_TIME = 600
    key = serialization.load_ssh_private_key(PRIV_KEY.encode(), password=None)
    payload = {
        "iss": "https://api.absent.cc",
        "sub": clientID,
        "exp": round(time.time()) + EXP_TIME,
        "iat": round(time.time()),
    }
    webtoken = jwt.encode(
        payload=payload,
        key=key,
        algorithm='RS256'
    )

    return webtoken

# Takes a ClientID and generates signed JWT for authentication purposes.
def generateRefreshToken(clientID: str) -> str:
    key = serialization.load_ssh_private_key(PRIV_KEY.encode(), password=None)
    payload = {
        "iss": "https://api.absent.cc",
        "sub": str(clientID),
        "iat": round(time.time()),
        "ref": True
    }
    webtoken = jwt.encode(
        payload=payload,
        key=key,
        algorithm='RS256'
    )

    return webtoken
