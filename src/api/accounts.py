from typing import Tuple
import jwt
import time
from api.helper import HelperFunctions
from dataTypes import schemas
from dataTypes import structs
from google.auth.transport import requests
from google.oauth2 import id_token
from cryptography.hazmat.primitives import serialization
from fastapi import Depends
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger
from database.crud import CRUD
from database.database import SessionLocal

class Accounts():

    def __init__(self):
        self.helper = HelperFunctions()

    # Top level accounts function used for creating account for new user.
    def createAccount(self, creds: dict) -> str:
        db = CRUD()
        name = creds['name'].split(' ', 1)
        if len(name) == 2:
            user = schemas.UserCreate(gid=int(creds['sub']), first=name[0], last=name[1])
        else:
            user = schemas.UserCreate(gid=int(creds['sub']), first=name[0])
        user = db.addUser(user)
        logger.info(f"Account created: {user.uid}")
        db.terminate()
        return user.uid

    # Top level accounts function used for creating a session.
    def initializeSession(self, uid: str) -> Tuple[str, str]:
        db = CRUD()
        session = schemas.SessionCreate(uid=uid)
        session = db.addSession(session)
        cid = f"{session.sid}.{uid}"
        jwt = self.generateToken(cid)
        logger.info(f"Session initialized: {uid}")
        db.terminate()
        return jwt, cid

    # Depends for checking credentials on each request.
    def verifyCredentials(self, creds: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> schemas.SessionReturn:
        session = self.validateToken(creds.credentials)
        return session

    def verifyRefreshToken(self, creds: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> str:
        cid = self.validateRefreshToken(creds.credentials)
        return cid

    def getDBSession(self):
        # Dependency
        db = CRUD()
        try:
            yield db
        finally:
            db.terminate()

    #
    # Token validation.
    #

    def checkEmail(self, email) -> bool:
        try:
            split = email.split('@')
            if split[0].isnumeric():
                return True
        except:
            self.helper.raiseError(401, "Invalid email", structs.ErrorType.AUTH)

    # Google IDToken check.
    def validateGoogleToken(self, token) -> dict:
        CLIENT_ID = "349911558418-9d07ptkk7pg7aqq58qkj5tshi8bq9s5v.apps.googleusercontent.com"
        NEWTON = "newton.k12.ma.us"
        try:
            idInfo = id_token.verify_oauth2_token(str(token), requests.Request(), CLIENT_ID)
            logger.info(f"Sucessful Google login: {idInfo['sub']}")
        except BaseException as error:
            logger.info(f"Invalid Google token POSTed.")
            self.helper.raiseError(401, error, structs.ErrorType.AUTH)
        try:
            if idInfo['hd'] != NEWTON:
                logger.info(f"Google token for a non-NPS account POSTed")
                self.helper.raiseError(401, "Not an NPS issued account", structs.ErrorType.AUTH)
        except BaseException:
            logger.info(f"Google token for a non-NPS account POSTed")
            self.helper.raiseError(401, "Not an NPS issued account", structs.ErrorType.AUTH)
        self.checkEmail(idInfo['email'])
        return idInfo

    # Our token check.
    def validateToken(self, jwt: str) -> schemas.SessionReturn:
        db = CRUD()
        creds = self.decodeToken(jwt)
        if creds == None:
            return None
        sub = creds['sub'].split('.')
        session = schemas.SessionReturn(uid=sub[1], sid=sub[0])
        session = db.getSession(session)
        db.terminate()
        if session != None:
            return session
        logger.info(f"Credential check failed: {sub}")
        self.helper.raiseError(401, "Invalid credentials", structs.ErrorType.AUTH)

    def validateRefreshToken(self, jwt: str) -> str:
        creds = self.decodeRefreshToken(jwt)
        try:
            if creds['ref'] == True:
                return creds['sub']
            else:
                return None
        except:
            return None

    # Building block for our token check.
    def decodeToken(self, webtoken: str) -> dict:
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
            self.helper.raiseError(401, error, structs.ErrorType.AUTH)
        return decoded

    # Building block for our token check.
    def decodeRefreshToken(self, webtoken: str) -> dict:
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
            self.helper.raiseError(401, error, structs.ErrorType.AUTH)
        return decoded

    #
    # Various functions for generating secrets and IDs.
    #

    # Takes a ClientID and generates signed JWT for authentication purposes.
    def generateToken(self, clientID: str) -> str:
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
    def generateRefreshToken(self, clientID: str) -> str:
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