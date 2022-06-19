import csv as c
import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends
from fuzzywuzzy import fuzz
from sqlalchemy.orm import Session

from src.dataTypes import models
from ....api import accounts, utils
from ....dataTypes import schemas, structs
from ....database import crud
from ....utils.prettifyTeacherName import prettifyTeacher

NNHS_FIRSTS = []
NNHS_LASTS = []

NSHS_FIRSTS = []
NSHS_LASTS = []


def readCSV(school: structs.SchoolName) -> bool:
    with open(f"data/{school}_teachers.csv") as f:
        csv = c.DictReader(f)
        for col in csv:
            globals()[f"{school}_FIRSTS"].append(col["First"])
            globals()[f"{school}_LASTS"].append(col["Last"])
    return True


readCSV(structs.SchoolName.NEWTON_NORTH)
readCSV(structs.SchoolName.NEWTON_SOUTH)

classDict = {
    0: [
        structs.SchoolBlock.A,
        structs.SchoolBlock.ADV,
        structs.SchoolBlock.B,
        structs.SchoolBlock.C,
        structs.SchoolBlock.D,
        structs.SchoolBlock.E,
    ],
    1: [
        structs.SchoolBlock.A,
        structs.SchoolBlock.B,
        structs.SchoolBlock.F,
        structs.SchoolBlock.G,
    ],
    2: [
        structs.SchoolBlock.C,
        structs.SchoolBlock.D,
        structs.SchoolBlock.E,
        structs.SchoolBlock.F,
    ],
    3: [
        structs.SchoolBlock.A,
        structs.SchoolBlock.B,
        structs.SchoolBlock.G,
        structs.SchoolBlock.E,
    ],
    4: [
        structs.SchoolBlock.C,
        structs.SchoolBlock.D,
        structs.SchoolBlock.F,
        structs.SchoolBlock.G,
    ],
    5: None,
    6: None,
}

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.get("/absences/", response_model=schemas.AbsenceList, status_code=200)
def getAbsenceList(
    date: datetime.date = None,
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials),
    db: Session = Depends(accounts.getDBSession),  # Initializes a DB.
    school: Optional[structs.SchoolName] = None,  # Initializes a school.
):
    if date is None:
        date = datetime.date.today()
    list: List[models.Absences] = crud.getAbsenceList(db, date, school)
    returnAbsences: List[schemas.AbsenceReturn] = [
        schemas.AbsenceReturn(
            length=absence.length, teacher=prettifyTeacher(absence.teacher), note=absence.note
        )
        for absence in list
    ]

    return schemas.AbsenceList(absences=returnAbsences, date=date)


@router.post("/autocomplete/", status_code=201, response_model=schemas.AutoComplete)
async def autocomplete(
    partialName: schemas.PartialName,
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials),
):
    if len(partialName.name) > 2:
        matches = []
        for index in range(len(globals()[f"{partialName.school}_FIRSTS"])):
            str = (
                globals()[f"{partialName.school}_FIRSTS"][index]
                + " "
                + globals()[f"{partialName.school}_LASTS"][index]
            )
            ratio = fuzz.partial_ratio(partialName.name.lower(), str.lower())
            if ratio > 80:
                matches.append(str)
        return schemas.AutoComplete(suggestions=matches)
    return None


@router.post("/validate/", response_model=schemas.TeacherValid, status_code=200)
async def isRealTeacher(
    partialName: schemas.PartialName,
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials),
):
    for index in range(len(globals()[f"{partialName.school}_FIRSTS"])):
        str = (
            globals()[f"{partialName.school}_FIRSTS"][index]
            + " "
            + globals()[f"{partialName.school}_LASTS"][index]
        )
        if partialName.name.lower() == str.lower():
            return schemas.TeacherValid(value=True, formatted=str)

    matches = None
    if len(partialName.name) > 2:
        matches = []
        for index in range(len(globals()[f"{partialName.school}_FIRSTS"])):
            str = (
                globals()[f"{partialName.school}_FIRSTS"][index]
                + " "
                + globals()[f"{partialName.school}_LASTS"][index]
            )
            ratio = fuzz.partial_ratio(partialName.name.lower(), str.lower())
            if ratio > 80:
                matches.append(str)

    return schemas.TeacherValid(value=False, suggestions=matches)
