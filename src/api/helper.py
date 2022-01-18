from fastapi import HTTPException
from dataStructs import *
from database.crud import CRUD

class HelperFunctions:
    def __init__(self):
        pass

    def raiseError(self, code, error, type: ErrorType):
        raise HTTPException(
            status_code=code,
            detail=f"{str(type)} - {error}"
        )   
    
    def returnStatus(self, message: str):
        return {'detail': message}
