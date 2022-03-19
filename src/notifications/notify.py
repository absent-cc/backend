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
        print(self.absences)

    def computeTotalClassesCancelled(self) -> Optional[List[schemas.NotificationBuild]]:
        # Compute the all the classes that are cancelled
        cancelledClasses: List[schemas.Class] = []

        if self.absences is None:
            return None

        for entry in self.absences:
            absence: schemas.AbsenceReturn = schemas.AbsenceReturn(
                teacher = schemas.TeacherReturn(
                    tid = entry.teacher.tid,
                    first = entry.teacher.first,
                    last = entry.teacher.last,
                    school = entry.teacher.school
                ),
                length = entry.length,
                note = entry.note
            )
            cancelled: schemas.Class = crud.getClassesByTeacherForDay(self.db, absence.teacher, self.date.weekday())
            print(cancelled)
            cancelledClasses.append(cancelled)
        
        return cancelledClasses

if __name__ == "__main__":
    test = Notify(structs.SchoolName.NEWTON_SOUTH)
    print("Running")
    test_cancelled = test.computeTotalClassesCancelled()
    for classs in test_cancelled:
        print(classs)
    