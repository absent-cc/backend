from src.database.database import SessionLocal
from ..dataTypes import structs
import datetime
from ..database import crud

class Notify():
    def __init__(self, school: structs.SchoolName, date: datetime.date = datetime.date.today()):
        self.db = SessionLocal()
        self.school = school
        self.date = date
        self.absences = crud.getAbsenceList(self.db, self.date, self.school)

    def notify(self):
