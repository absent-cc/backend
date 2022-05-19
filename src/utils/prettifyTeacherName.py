import re
from typing import List, Tuple

from src.dataTypes.schemas import TeacherReturn
from src.database.database import SessionLocal

splitTable = "\s|-|_|\."


def prettifyTeacher(teacher: TeacherReturn) -> TeacherReturn:

    prettyFirst, prettyLast = prettifyName(str(teacher.first), str(teacher.last))

    if hasattr(teacher, "tid"): 
        return TeacherReturn(
            tid=teacher.tid, first=prettyFirst, last=prettyLast, school=teacher.school
        )
    else:
        return TeacherReturn(first=prettyFirst, last=prettyLast, school=teacher.school)

def prettifyName(first: str, last: str) -> Tuple[str, str]:
    first_split = re.split(splitTable, first.lower())
    last_split = re.split(splitTable, last.lower())

    first_delim = re.findall(splitTable, first.lower())
    last_delim = re.findall(splitTable, last.lower())

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

    return prettyFirst, prettyLast

# if __name__ == "__main__":
#     # print(prettify(TeacherBase(first="jimmy-john", last="smith-jr")))

#     from ..database import crud
#     from ..dataTypes import models, schemas
#     from ..dataTypes import structs
#     import datetime

#     db = SessionLocal()

#     school = structs.SchoolName.NEWTON_SOUTH
#     date = datetime.date.today()

#     list: List[models.Absence] = crud.getAbsenceList(db, date, school)
#     returnAbsences: List[schemas.AbsenceReturn] = [
#         schemas.AbsenceReturn(
#             length=absence.length, teacher=prettify(absence.teacher), note=absence.note
#         )
#         for absence in list
#     ]

#     print(returnAbsences)
