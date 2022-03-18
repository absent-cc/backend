from src.database.database import SessionLocal
from ..dataTypes import structs, models
import datetime
from ..database import crud

from typing import Optional, List, Tuple
class Notify():
    def __init__(self, school: structs.SchoolName, date: datetime.date = datetime.date.today()):
        self.db = SessionLocal()
        self.school = school
        self.date = date
        self.absences: Optional[List[models.Absence]] = crud.getAbsenceList(self.db, self.date, self.school)

    def computeTotalClassesCancelled(self):
        pass
