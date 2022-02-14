from fastapi import APIRouter, Depends
from sqlalchemy import true
from sqlalchemy.orm import Session

from ....api import accounts
from ....database import crud
from ....dataTypes import schemas

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/info", response_model=schemas.Analytics)
def getAnalytics(
    db: Session = Depends(accounts.getDBSession)
) -> schemas.Analytics:
    userCount = crud.getUserCount(db)
    absences = crud.getAbsencesCount(db)
    return schemas.Analytics(userCount=userCount, totalAbsences=absences)

@router.post("/canceled", response_model=schemas.Bool)
async def updateAbsences(
    cancelledClasses: list[schemas.CanceledClassCreate],
    db: Session = Depends(accounts.getDBSession),
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials)
) -> schemas.Bool:
    for cancelledClass in cancelledClasses:
        try:
            return_val = crud.addCanceledClass(db, cancelledClass)
            return schemas.Bool(value=return_val)
        except Exception:
            print("Absence already exists. Will not add again.")
            return schemas.Bool(success=False)