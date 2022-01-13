import secrets
import jwt
import time
from uuid import uuid4
from api.helper import HelperFunctions
from dataStructs import *
from database.databaseHandler import DatabaseHandler
from google.auth.transport import requests
from google.oauth2 import id_token
from cryptography.hazmat.primitives import serialization
from fastapi import Depends
from fastapi.security.http import HTTPBearer, HTTPAuthorizationCredentials


class Accounts():

    def __init__(self):
        self.database = DatabaseHandler()
        self.helper = HelperFunctions()

    # Top level accounts function used for creating account for new user.
    def createAccount(self, creds: dict):
        name = creds['name'].split(' ', 1)
        if len(name) == 2:
            student = Student(uid=self.generateUUID(), gid=int(creds['sub']), first=name[0], last=name[1])
        else:
            student = Student(uid=self.generateUUID(), gid=int(creds['sub']), first=name[0])
        
        return self.database.addStudent(student)

    # Top level accounts function used for creating a session.
    def initializeSession(self, uuid: UUID):
        database = DatabaseHandler()
        clientID = self.generateClientID(uuid)
        session = Session(cid=clientID, startTime=datetime.now())
        database.addSession(session)

        jwt = self.generateJWT(clientID)
        return jwt

    # Depends for checking credentials on each request.
    def verifyCredentials(self, creds: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        session = self.validateToken(creds.credentials)
        return session

    #
    # Token validation.
    #

    # Google IDToken check.
    def validateGoogleToken(self, token):
        CLIENT_ID = "349911558418-25qq88oirls8unm6mln5kb41fn2shkns.apps.googleusercontent.com"
        NEWTON = "newton.k12.ma.us"
        try:
            idInfo = id_token.verify_oauth2_token(str(token), requests.Request(), CLIENT_ID)
        except BaseException as error:
            self.helper.raiseError(401, error, ErrorType.AUTH)
        try:
            if idInfo['hd'] != NEWTON:
                self.helper.raiseError(401, "Not an NPS issued account", ErrorType.AUTH)
        except BaseException:
            self.helper.raiseError(401, "Not an NPS issued account", ErrorType.AUTH)
    
        return idInfo
    # Our token check.
    def validateToken(self, jwt: str):
        database = DatabaseHandler()
        creds = self.decodeJWT(jwt)
        if creds == None:
            return None
        inSessions = database.getSession(Session(cid=creds['sub'], startTime=None))
        if inSessions != None:
            #if database.getSession(Session(None, None, None, None, None, inSessions)).start_time :
            return inSessions
        self.helper.raiseError(401, "Invalid Credentials.", ErrorType.AUTH)

    # Building block for our token check.
    def decodeJWT(self, webtoken: str):
        SECRET = open('.ssh/id_rsa.pub', 'r').read()
        key = serialization.load_ssh_public_key(SECRET.encode())
        try:
            decoded = jwt.decode(
                webtoken,
                key=key,
                options={"require": ["exp", "iss", "sub", "aud", "iat"]},
                audience="https://api.absent.cc",
                algorithms=['RS256',]
                )
        except BaseException as error:
            self.helper.raiseError(401, error, ErrorType.AUTH)
        return decoded

    #
    # Various functions for generating secrets and IDs.
    #

    # Generates a ClientID (unique to each session).
    def generateClientID(self, uuid: UUID):
        return secrets.token_hex(8) + "." + str(uuid)
    
    # Generates UUID for user management.
    def generateUUID(self):
        return uuid4()

    # Takes a ClientID and generates signed JWT for authentication purposes.
    def generateJWT(self, clientID: str):
        SECRET = open('.ssh/id_rsa', 'r').read()
        EXP_TIME = 2592000
        key = serialization.load_ssh_private_key(SECRET.encode(), password=None)
        payload = {
            "iss": "https://api.absent.cc",
            "sub": clientID,
            "aud": "https://api.absent.cc",
            "exp": round(time.time()) + EXP_TIME,
            "iat": round(time.time()),
        }
        webtoken = jwt.encode(
            payload=payload,
            key=key,
            algorithm='RS256'
        )

        return webtoken

    def updateSchedule(self, student, schedule: Schedule):
        return self.database.updateStudentClasses(student, schedule)

    def updateProfile(self, student, profile):
        return self.database.updateStudentInfo(student, profile)


