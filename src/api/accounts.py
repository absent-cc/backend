import secrets
import base64
from database.databaseHandler import DatabaseHandler
from dataStructs import *
from datetime import datetime

class Authenticator:

    def __init__(self):
        pass

    def validateGoogleToken(self, token):
        # OAUTH CODE GOES HERE
        return True

    def initializeSession(self, uuid: UUID):
        database = DatabaseHandler()
        token = self.generateToken()
        clientID = self.generateClientID(uuid)
        session = Session(uuid, clientID, token, datetime.now())

        database.addSession(session)
        return session

    def generateToken(self):
        return Token(secrets.token_urlsafe(64))

    def generateClientID(self, uuid: UUID):
        return ClientID(secrets.token_hex(8) + "." + str(uuid))

    def validateToken(self, clientID: ClientID, token: Token):
        database = DatabaseHandler()
        inSessions = database.getSessionID(Session(None, clientID, token, None))
        if inSessions != None:
            #if database.getSession(Session(None, None, None, None, None, inSessions)).start_time :
            return True
        return False

    
    

