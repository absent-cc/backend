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
    absent_teachers: list[schemas.AbsenceCreate],
    db: Session = Depends(accounts.getDBSession)
) -> schemas.Bool:
    for entry in absent_teachers:
        print(entry)
        teacher = entry.teacher
        date = entry.date

        try:
            print(crud.addAbsence(db, teacher, date=date))
        except:
            print("Failed to add absence.")
            pass
    return schemas.Bool(success=True)
