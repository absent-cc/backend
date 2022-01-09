import secrets
from database.databaseHandler import DatabaseHandler
from dataStructs import *
from datetime import datetime
from google.oauth2 import id_token
from google.auth.transport import requests
from uuid import uuid4

class Authenticator:

    def __init__(self):
        pass

    def validateGoogleToken(self, token):
        gClientID = "349911558418-5joq5quivkmpbkl8nnu89rn8upa6itr1.apps.googleusercontent.com"
        try:
            idInfo = id_token.verify_oauth2_token(str(token), requests.Request(), gClientID)
            return idInfo
        except ValueError:
            return None

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
    
    def generateUUID(self):
        return uuid4()

    def validateToken(self, clientID: ClientID, token: Token):
        database = DatabaseHandler()
        inSessions = database.getSessionID(Session(None, clientID, token, None))
        if inSessions != None:
            #if database.getSession(Session(None, None, None, None, None, inSessions)).start_time :
            return True
        return False

    
    

