from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ....api import accounts
from ....database import crud
from ....dataTypes import schemas

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/info", response_model=schemas.Analytics)
def getAnalytics(
    db: Session = Depends(accounts.getDBSession)
):
    userCount = crud.getUserCount(db)
    absences = crud.getAbsencesCount(db)
    return schemas.Analytics(userCount=userCount, totalAbsences=absences)
