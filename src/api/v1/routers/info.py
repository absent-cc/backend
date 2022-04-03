import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.dataTypes import structs

from ....api import accounts, utils
from ....database import crud

router = APIRouter(prefix="/info", tags=["Info"])

@router.get("/schedule/", response_model=structs.SchoolDay, status_code=200)
async def getSchedule(
    date: datetime.date = None,
    db: Session = Depends(accounts.getDBSession), # Initializes a DB. 
):
    if date == None:
        date = datetime.date.today()
    
    specialDayInDB = crud.getSpecialDay(db, date=date)

    if specialDayInDB != None:
        return structs.SpecialDay(
            date=date,
            name=specialDayInDB.name,
            schedule=specialDayInDB.schedule,
            note=specialDayInDB.note
        )
    
    return structs.NormalDay(
        date=date,
        schedule=structs.SchoolBlocksOnDayWithTimes()[date.weekday()]
    )