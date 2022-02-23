import csv as c
import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Body
from fuzzywuzzy import fuzz
from sqlalchemy.orm import Session

from ....api import accounts, utils
from ....database import crud
from ....dataTypes import schemas, structs

NNHS_FIRSTS = []
NNHS_LASTS = []

NSHS_FIRSTS = []
NSHS_LASTS = []

def readCSV(school: structs.SchoolName) -> bool:
    with open(f'data/{school}_teachers.csv') as f:
        csv = c.DictReader(f)
        for col in csv:
            globals()[f"{school}_FIRSTS"].append(col['First'])
            globals()[f"{school}_LASTS"].append(col['Last'])
    return True

readCSV(structs.SchoolName.NEWTON_NORTH)
readCSV(structs.SchoolName.NEWTON_SOUTH)

classDict = {
    0: [structs.SchoolBlock.A, structs.SchoolBlock.ADV, structs.SchoolBlock.B, structs.SchoolBlock.C, structs.SchoolBlock.D, structs.SchoolBlock.E],
    1: [structs.SchoolBlock.A, structs.SchoolBlock.B, structs.SchoolBlock.F, structs.SchoolBlock.G],
    2: [structs.SchoolBlock.C, structs.SchoolBlock.D, structs.SchoolBlock.E, structs.SchoolBlock.F],
    3: [structs.SchoolBlock.A, structs.SchoolBlock.B, structs.SchoolBlock.G, structs.SchoolBlock.E],
    4: [structs.SchoolBlock.C, structs.SchoolBlock.D, structs.SchoolBlock.F, structs.SchoolBlock.G],
    5: None,
    6: None
}

router = APIRouter(prefix="/teachers", tags=["Teachers"])

@router.get("/absences/", response_model=schemas.AbsenceList, status_code=200)
def getAbsenceList(
    date: Optional[datetime.date] = datetime.date.today(),
    db: Session = Depends(accounts.getDBSession) # Initializes a DB. 
):  
    list = crud.getAbsenceList(db, date)
    return schemas.AbsenceList(absences=list)

@router.get("/classes/", response_model=schemas.ClassList, status_code=200)
async def getClassList(date: datetime.date):
    try:
        return schemas.ClassList(classes=classDict[date.weekday()])
    except:
        utils.raiseError(422, "Invalid date", structs.ErrorType.PAYLOAD)

@router.post("/autocomplete/", status_code=201, response_model=schemas.AutoComplete)
async def autocomplete(partialName: schemas.PartialName):
    if len(partialName.name) > 2:
        matches = []
        for index in range(len(globals()[f"{partialName.school}_FIRSTS"])):
            str = globals()[f"{partialName.school}_FIRSTS"][index] + " " + globals()[f"{partialName.school}_LASTS"][index]
            ratio = fuzz.partial_ratio(partialName.name.lower(), str.lower())
            if ratio > 80:
                matches.append(str)
        return schemas.AutoComplete(suggestions=matches)
    return None

@router.post("/validate/", response_model=schemas.TeacherValid, status_code=200)
async def isRealTeacher(partialName: schemas.PartialName):
    for index in range(len(globals()[f"{partialName.school}_FIRSTS"])):
        str = globals()[f"{partialName.school}_FIRSTS"][index] + " " + globals()[f"{partialName.school}_LASTS"][index]
        if partialName.name.lower() == str.lower():
            return schemas.TeacherValid(value=True, formatted=str)

    matches = None
    if len(partialName.name) > 2:
        matches = []
        for index in range(len(globals()[f"{partialName.school}_FIRSTS"])):
            str = globals()[f"{partialName.school}_FIRSTS"][index] + " " + globals()[f"{partialName.school}_LASTS"][index]
            ratio = fuzz.partial_ratio(partialName.name.lower(), str.lower())
            if ratio > 80:
                matches.append(str)

    return schemas.TeacherValid(value=False, suggestions=matches)

