import datetime
from webbrowser import get

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.dataTypes import structs, schemas
from ....utils.weekGen import weekDayGenerator
from ....api import accounts
from ....database import crud

router = APIRouter(prefix="/info", tags=["Info"])

from typing import Optional, List

@router.get("/schedule/day", response_model=schemas.SchoolDay, status_code=200)
def getSchedule(
    date: datetime.date = None,
    db: Session = Depends(accounts.getDBSession),  # Initializes a DB.
):
    if date is None:
        date = datetime.date.today()

    specialDayInDB = crud.getSpecialDay(db, date=date)

    if specialDayInDB is not None:
        return schemas.SpecialDay(
            date=date,
            name=specialDayInDB.name,
            schedule=specialDayInDB.schedule,
            note=specialDayInDB.note,
        )

    return schemas.NormalDay(
        date=date, schedule=structs.SchoolBlocksOnDayWithTimes()[date.weekday()]
    )

@router.get("/schedule/week/", response_model=List[schemas.SchoolDay], status_code=200)
def weekPeek(
    date: Optional[datetime.date] = None,
    db: Session = Depends(accounts.getDBSession),  # Initializes a DB.
):
    if date is None:
        date = datetime.date.today()
    
    year, week, weekday = date.isocalendar()

    if weekday == 5 or weekday == 6:
        week += 1
    
    # Generate weekdays to iterate over:
    weekdays: List[datetime.date] = weekDayGenerator(year, week)
    
    return [getSchedule(day, db) for day in weekdays]