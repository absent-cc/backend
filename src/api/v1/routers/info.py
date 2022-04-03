import datetime
from fastapi import APIRouter

from src.dataTypes import structs


router = APIRouter(prefix="/info", tags=["Info"])

@router.get("/schedule/", response_model=structs.ScheduleWithTimes, status_code=200)
async def getSchedule(
    date: datetime.date = None,
):
    if date == None:
        date = datetime.date.today()
    # Check if its a special day
    return structs.SchoolBlocksOnDayWithTimes()[date.weekday()]