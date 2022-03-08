from src.dataTypes.schemas import TeacherBase, TeacherCreate
import re
from typing import List

from src.database.database import SessionLocal

splitTable = "\s|-|_|\."
def prettify(teacher: TeacherBase) -> TeacherBase:
    
    first_split = re.split(splitTable, teacher.first.lower())
    last_split = re.split(splitTable, teacher.last.lower())

    first_delim = re.findall(splitTable, teacher.first.lower())
    last_delim = re.findall(splitTable, teacher.last.lower())

    def prettyCompile(splits: list, delimitingChar: List[str]) -> str:
        returnStr = ""
        counter = 0
        for part in splits:
            returnStr += part.capitalize()
            if counter < len(delimitingChar):
                returnStr += delimitingChar[counter]
            counter += 1
        return returnStr

    prettyFirst = prettyCompile(first_split, first_delim)
    prettyLast = prettyCompile(last_split, last_delim)

    return TeacherBase(first=prettyFirst, last=prettyLast)

if __name__ == "__main__":
    # print(prettify(TeacherBase(first="jimmy-john", last="smith-jr")))

    from ..database import crud
    from ..dataTypes import models, schemas
    from ..dataTypes import structs
    import datetime

    db = SessionLocal()
    
    school = structs.SchoolName.NEWTON_SOUTH
    date = datetime.date.today()

    list: List[models.Absence] = crud.getAbsenceList(db, date, school)
    returnAbsences: List[schemas.AbsenceReturn] = [ schemas.AbsenceReturn(length=absence.length, teacher=prettify(absence.teacher), note=absence.note) for absence in list ]

    print(returnAbsences) 