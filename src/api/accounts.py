import jwt
import time
import api.utils as utils
import database.crud as crud
from dataTypes import schemas
from dataTypes import structs
from google.auth.transport import requests
from google.oauth2 import id_token
from cryptography.hazmat.primitives import serialization
from fastapi import Depends
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger
from database.database import SessionLocal

def getDBSession():
    # Dependency
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Depends for checking credentials on each request.
def verifyCredentials(creds: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db = Depends(getDBSession)) -> schemas.SessionReturn:
    creds = decodeToken(creds.credentials)
    if creds == None:
        return None
    sub = creds['sub'].split('.')
    session = schemas.SessionReturn(uid=sub[1], sid=sub[0])
    session = crud.getSession(db, session)
    if session != None:
        return session
    logger.info(f"Credential check failed: {sub}")
    utils.raiseError(401, "Invalid credentials", structs.ErrorType.AUTH)
    return None

def verifyRefreshToken(creds: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> str:
    cid = validateRefreshToken(creds.credentials)
    return cid

#
# Token validation.
#

# Google IDToken check.
def validateGoogleToken(token) -> dict:
    CLIENT_ID = "349911558418-9d07ptkk7pg7aqq58qkj5tshi8bq9s5v.apps.googleusercontent.com"
    NEWTON = "newton.k12.ma.us"
    try:
        idInfo = id_token.verify_oauth2_token(token.token, requests.Request(), CLIENT_ID)
        logger.info(f"Sucessful Google login: {idInfo['sub']}")
    except BaseException as error:
        logger.info(f"Invalid Google token POSTed.")
        utils.raiseError(401, error, structs.ErrorType.AUTH)
    try:
        if idInfo['hd'] != NEWTON:
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
    SECRET = open('.ssh/id_rsa.pub', 'r').read()
    key = serialization.load_ssh_public_key(SECRET.encode())
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
    SECRET = open('.ssh/id_rsa.pub', 'r').read()
    key = serialization.load_ssh_public_key(SECRET.encode())
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
    SECRET = open('.ssh/id_rsa', 'r').read()
    EXP_TIME = 600
    key = serialization.load_ssh_private_key(SECRET.encode(), password=None)
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
    SECRET = open('.ssh/id_rsa', 'r').read()
    key = serialization.load_ssh_private_key(SECRET.encode(), password=None)
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