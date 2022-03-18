from src.database.database import SessionLocal
from ..dataTypes import structs, models, schemas
import datetime
from ..database import crud

from typing import Optional, List, Tuple
class Notify():
    def __init__(self, school: structs.SchoolName, date: datetime.date = datetime.date.today()):
        self.db = SessionLocal()
        self.school = school
        self.date = date
        self.absences: Optional[List[models.Absence]] = crud.getAbsenceList(self.db, self.date, self.school)

    def computeTotalClassesCancelled(self) -> Optional[List[schemas.NotificationBuild]]:
        # Compute the all the classes that are cancelled
        cancelledClasses: List[schemas.Class] = []

        if self.absences is None:
            return None

        for entry in self.absences:
            absence: schemas.AbsenceReturn = schemas.AbsenceReturn(
                tid=entry.tid,
                first=entry.first,
                last=entry.last,
                length=entry.length,
                date=entry.date,
                note=entry.note
            )
            cancelled: schemas.Class = crud.getClassesByTeacherForDay(self.db, absence.teacher, self.date.weekday())
            cancelledClasses.append(cancelled)
        
        return cancelledClasses

if __name__ == "__main__":
    test = Notify(structs.SchoolName.NEWTON_SOUTH, datetime.date.today())
    print(test.computeTotalClassesCancelled())
            