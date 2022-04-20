from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ....api import accounts
from ....dataTypes import schemas
from ....database import crud

router = APIRouter(prefix="/badges", tags=["Shields.io Badges"])


@router.get("/users/count/", response_model=schemas.AbsencesBadge)
def getUserCount(
    db: Session = Depends(accounts.getDBSession),
) -> schemas.UserCountBadge:
    userCount = crud.getUserCount(db)
    return schemas.UserCountBadge(message=str(userCount))


@router.get("/absences/count/", response_model=schemas.AbsencesBadge)
def getAbsences(db: Session = Depends(accounts.getDBSession)) -> schemas.AbsencesBadge:
    absences = crud.getAbsencesCount(db)
    return schemas.AbsencesBadge(message=str(absences))


@router.get("/classes/count/", response_model=schemas.ClassCountBadge)
def getNumberOfClasses(db: Session = Depends(accounts.getDBSession)) -> schemas.ClassCountBadge:
    classes = crud.getClassesCount(db)
    return schemas.ClassCountBadge(message=str(classes))