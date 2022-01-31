from fastapi import HTTPException
from dataTypes import structs

def raiseError(code, error, type: structs.ErrorType):
    raise HTTPException(
        status_code=code,
        detail=f"{str(type)} - {error}"
    )   

def returnStatus(message: str):
    return {'detail': message}

    
