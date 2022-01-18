from fastapi import HTTPException
from dataTypes import structs
from database.crud import CRUD

class HelperFunctions:
    def __init__(self):
        pass

    def raiseError(self, code, error, type: structs.ErrorType):
        raise HTTPException(
            status_code=code,
            detail=f"{str(type)} - {error}"
        )   
    
    def returnStatus(self, message: str):
        return {'detail': message}
