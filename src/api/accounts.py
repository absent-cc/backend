import secrets
from database.databaseHandler import DatabaseHandler

class Authenticator:

    def __init__(self):
        pass

    def initializeSession(self):
        token = self.generateToken()
                

    def generateToken():
        return secrets.token_urlsafe(64)

    def validateToken(self):
        pass
    

