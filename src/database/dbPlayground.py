from . import crud

from .database import SessionLocal
from ..dataTypes import structs
from datetime import date
db = SessionLocal()

# specialDay = structs.SpecialDay(
#     date=date(2020, 1, 1),
#     name="New Year's Day",
#     schedule=[structs.SchoolBlock.A, structs.SchoolBlock.B, structs.SchoolBlock.C, structs.SchoolBlock.D, structs.SchoolBlock.E],
#     notes = "Happy New Year!",
#     )

    
# crud.addSpecialDay(db, )

if __name__ == "__main__":
    print(structs.SchoolBlocksOnDayWithTimes())