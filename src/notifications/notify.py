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
        self.classDict = {
            0: [structs.SchoolBlock.A, structs.SchoolBlock.ADV, structs.SchoolBlock.B, structs.SchoolBlock.C, structs.SchoolBlock.D, structs.SchoolBlock.E],
            1: [structs.SchoolBlock.A, structs.SchoolBlock.B, structs.SchoolBlock.F, structs.SchoolBlock.G],
            2: [structs.SchoolBlock.C, structs.SchoolBlock.D, structs.SchoolBlock.E, structs.SchoolBlock.F],
            3: [structs.SchoolBlock.A, structs.SchoolBlock.B, structs.SchoolBlock.G, structs.SchoolBlock.E],
            4: [structs.SchoolBlock.C, structs.SchoolBlock.D, structs.SchoolBlock.F, structs.SchoolBlock.G],
            5: None,
            6: None
        }

    def buildNotifications(self):
        validBlocks = self.classDict[self.date.weekday()]
        absences = crud.getAbsenceList(self.db, self.date, self.school)
        for absence in absences:
            for cls in absence.teacher.classes:
                if cls.block in validBlocks:
                    print(cls)

if __name__ == "__main__":
    test = Notify(structs.SchoolName.NEWTON_SOUTH, datetime.date.today())
    print(test.buildNotifications())
            