import secrets
from uuid import uuid4
from database.databaseHandler import DatabaseHandler
from dataStructs import *
from datetime import datetime

class Authenticator:

    def __init__(self):
        pass

    def validateGoogleToken(self, token):
        # OAUTH CODE GOES HERE
        return True

    def initializeSession(self, uuid):
        database = DatabaseHandler()
        strtoken = self.generateToken()
        try:
            token = Token(strtoken)
        except ValueError:
            return None
        session = Session(uuid, token, datetime.now())

        database.addSession(session)
        return True

    def generateToken(self):
        return secrets.token_urlsafe(64)

    def validateToken(self, token: Token, uuid: UUID):
        database = DatabaseHandler()
        if database.getSessionID(Session(uuid, token, None)):
            return True
        return False
    

