from . import crud

from .database import SessionLocal
from ..dataTypes import structs
from datetime import date, time
db = SessionLocal()

crud.reset(db)
specialDay = structs.SpecialDay(
    date=date(2020, 1, 1),
    name="New Year's Day",
    schedule = structs.SchoolBlocksOnDayWithTimes()[6],
    note = "Happy New Year!",
    )

print(crud.addSpecialDay(db, specialDay=specialDay))
returnVal = crud.getSpecialDay(db, date=specialDay.date)
print(returnVal.schedule)

# if __name__ == "__main__":
#     print(structs.SchoolBlocksOnDayWithTimes())