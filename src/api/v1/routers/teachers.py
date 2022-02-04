import csv as c

from fastapi import APIRouter, Depends
from fuzzywuzzy import fuzz
from sqlalchemy.orm import Session

from ....api import accounts
from ....database import crud
from ....dataTypes import schemas, structs

NNHS_FIRSTS = []
NNHS_LASTS = []

NSHS_FIRSTS = []
NSHS_LASTS = []

def readCSV(school: structs.SchoolName) -> bool:
    with open(f'data/{school}_teachers.csv') as f:
        csv = c.DictReader(f)
        print(f"{school}_FIRSTS")
        for col in csv:
            globals()[f"{school}_FIRSTS"].append(col['First'])
            globals()[f"{school}_LASTS"].append(col['Last'])
    return True

readCSV(structs.SchoolName.NEWTON_NORTH)
readCSV(structs.SchoolName.NEWTON_SOUTH)

router = APIRouter(prefix="/teachers", tags=["Teachers"])

@router.get("/absences", response_model=schemas.AbsenceList, status_code=200)
def getAbsenceList(
    db: Session = Depends(accounts.getDBSession) # Initializes a DB. 
):
    list = crud.getAbsenceList(db)
    return schemas.AbsenceList(absences=list)

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

@router.post("/validate/", response_model=schemas.Valid, status_code=200)
async def isRealTeacher(partialName: schemas.PartialName):
    for index in range(len(globals()[f"{partialName.school}_FIRSTS"])):
        str = globals()[f"{partialName.school}_FIRSTS"][index] + " " + globals()[f"{partialName.school}_LASTS"][index]
        if partialName.name.lower() == str.lower():
            return schemas.Valid(value=True)
    return schemas.Valid(value=True)
