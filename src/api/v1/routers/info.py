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
    
    if weekday == 6 or weekday == 7: 
        # Remember these are ISO Cal days, so sunday is 7, saturday is 6.
        week += 1
    
    # Generate weekdays to iterate over:
    weekdays: List[datetime.date] = weekDayGenerator(year, week)
    
    return [getSchedule(day, db) for day in weekdays]

@router.get("/announcements/latest", response_model=List[schemas.AnnouncementReturn], status_code=200)
def getAnnouncements(
    db: Session = Depends(accounts.getDBSession),  # Initializes a DB.
    school: Optional[structs.SchoolName] = None,
    amount: int = 5,
):
    return crud.getAnnouncements(db, school, amount)

@router.get("/announcements/date", response_model=List[schemas.AnnouncementReturn], status_code=200)
def getAnnouncements(
    db: Session = Depends(accounts.getDBSession),  # Initializes a DB.
    school: Optional[structs.SchoolName] = None,
    date: Optional[datetime.date] = None,
):
    if date == None:
        date = datetime.date.today()
    
    return crud.getAnnouncementByDateAndSchool(db, date, school)