from . import crud

from .database import SessionLocal
from ..dataTypes import structs
from datetime import date, time
db = SessionLocal()

# specialDay = structs.SpecialDay(
#     date=date(2022, 4, 3),
#     name="New Year's Day",
#     schedule = structs.SchoolBlocksOnDayWithTimes()[0],
#     note = "Happy New Year!",
#     )

# print(crud.addSpecialDay(db, specialDay=specialDay))
# returnVal = crud.getSpecialDay(db, date=specialDay.date)
# print(returnVal.schedule)
# print(returnVal.schedule.blocks())

for day in structs.SchoolBlocksOnDayWithTimes().values():
    print(day)

# if __name__ == "__main__":
#     print(structs.SchoolBlocksOnDayWithTimes())