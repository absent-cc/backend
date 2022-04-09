import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.dataTypes import structs, schemas
from ....api import accounts
from ....database import crud

router = APIRouter(prefix="/info", tags=["Info"])


@router.get("/schedule/", response_model=schemas.SchoolDay, status_code=200)
async def getSchedule(
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
