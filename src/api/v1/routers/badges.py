from email import message
from fastapi import APIRouter, Depends
from sqlalchemy import true
from sqlalchemy.orm import Session

from ....api import accounts
from ....database import crud
from ....dataTypes import schemas

from typing import List

router = APIRouter(prefix="/badges", tags=["Shields.io Badges"])

@router.get("/user/count", response_model=schemas.AbsencesBadge)
def getUserCount(
    db: Session = Depends(accounts.getDBSession)
) -> schemas.UserCountBadge:
    userCount = crud.getUserCount(db)
    return schemas.UserCountBadge(
        message=str(userCount)
        )
    
@router.get("/absences/count", response_model=schemas.AbsencesBadge)
def getAbsences(
    db: Session = Depends(accounts.getDBSession)
) -> schemas.AbsencesBadge:
    absences = crud.getAbsencesCount(db)
    return schemas.AbsencesBadge(
        message=str(absences)
        )

@router.get("/classes/count", response_model=schemas.AbsencesBadge)
def getClasses(
    db: Session = Depends(accounts.getDBSession)
) -> schemas.AbsencesBadge:
    classes = crud.getClassesCount(db)
    return schemas.AbsencesBadge(
        message=str(classes)
        )