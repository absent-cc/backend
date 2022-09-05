import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.dataTypes import structs, schemas
from ....utils.weekGen import weekDayGenerator  # type: ignore
from ....api import accounts                    # type: ignore
from ....database import crud                   # type: ignore
from ....api import utils                       # type: ignore

router = APIRouter(prefix="/info", tags=["Info"])

from typing import Optional, List


@router.get("/schedule/day", response_model=schemas.SchoolDay, status_code=200)
def getSchedule(
    date: datetime.date = None,
    school: Optional[structs.SchoolName] = None,
    db: Session = Depends(accounts.getDBSession),  # Initializes a DB.
):
    if date is None:
        date = datetime.date.today()

    specialDayInDB = crud.getSpecialDay(db, date, school)

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
    school: Optional[structs.SchoolName] = None,
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

    return [getSchedule(day, db, school) for day in weekdays]


# @router.get("/announcements/slice", response_model=List[schemas.AnnouncementReturn], status_code=200)
# def getAnnouncementsWithSlice(
#     db: Session = Depends(accounts.getDBSession),  # Initializes a DB.
#     school: Optional[structs.SchoolName] = None,
#     top: Optional[int] = None,
#     bottom: Optional[int] = None,
# ):
#     if top is None:
#         top = 10
#     if bottom is None:
#         bottom = 0

#     if top < 0 or bottom < 0:
#         utils.raiseError(406, "Amount is negative", structs.ErrorType.PAYLOAD)

#     return crud.getAnnouncements(db, school, top, bottom)


@router.get(
    "/announcements/",
    response_model=List[schemas.AnnouncementReturn],
    status_code=200,
)
def getAnnouncementsByPage(
    db: Session = Depends(accounts.getDBSession),  # Initializes a DB.
    school: Optional[structs.SchoolName] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
):
    if page is None:
        page = 0
    if page < 0:
        utils.raiseError(
            406, "Invalid value: Page is negative", structs.ErrorType.PAYLOAD
        )

    if page_size is None:
        page_size = 5  # Sets default for page size.
    if page_size < 0:
        utils.raiseError(
            406, "Invalid value: Page size is negative", structs.ErrorType.PAYLOAD
        )

    return crud.getAnnouncementsByPage(db, page, page_size, school)


@router.get(
    "/announcements/bydate/",
    response_model=List[schemas.AnnouncementReturn],
    status_code=200,
)
def getAnnouncementsByDate(
    db: Session = Depends(accounts.getDBSession),  # Initializes a DB.
    school: Optional[structs.SchoolName] = None,
    date: Optional[datetime.date] = None,
):

    if date == None:
        date = datetime.date.today()

    return crud.getAnnouncementByDateAndSchool(db, date, school)
