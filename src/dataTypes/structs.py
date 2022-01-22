from enum import Enum
from dataclasses import dataclass
from typing import List
from pydantic import BaseModel

#
# SCHOOL ENUMS (BLOCK AND NAME) 
#

class SchoolNameMapper(dict):
    def __init__(self):
        super().__init__()
        self.update({
            "NSHS": SchoolName.NEWTON_SOUTH,
            "NNHS": SchoolName.NEWTON_NORTH,
            None: None
        })

class SchoolName(str, Enum):
    NEWTON_SOUTH: str = "NSHS"
    NEWTON_NORTH: str = "NNHS"

class SchoolBlock(str, Enum):
    A: str = "A"
    ADV: str = "ADVISORY"
    B: str = "B"
    C: str = "C"
    D: str = "D"
    E: str = "E"
    F: str = "F"
    G: str = "G"

class BlockMapper(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update({
            SchoolBlock.A: "A",
            SchoolBlock.ADV: "ADV",
            SchoolBlock.B: "B",
            SchoolBlock.C: "C",
            SchoolBlock.D: "D",
            SchoolBlock.E: "E",
            SchoolBlock.F: "F",
            SchoolBlock.G: "G"
        })
    
class ReverseBlockMapper(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update({
            "A": SchoolBlock.A,
            "ADV": SchoolBlock.ADV,
            "ADVISORY": SchoolBlock.ADV,
            "B": SchoolBlock.B,
            "C": SchoolBlock.C,
            "D": SchoolBlock.D,
            "E": SchoolBlock.E,
            "F": SchoolBlock.F,
            "G": SchoolBlock.G,
        })

#
# API ENUMS
#

class ErrorTypeMapper(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update({
            ErrorType.AUTH: "Authentication Error",
            ErrorType.DB: "Database Error",
            ErrorType.PAYLOAD: "Payload Error"
        })

class ErrorType(Enum):
    AUTH = "Authentication Error"
    DB = "Database Error"
    PAYLOAD = "Payload Error"
    def __str__(self) -> str:
        mapper = ErrorTypeMapper()
        return mapper[self]

#
# STUDENT, TEACHER, CLASSTEACHERS(CUSTOM SET), ABSENTTEACHER, AND SCHEDULE OBJECTS
#

class NotPresent(Enum):
    TRUE = None

@dataclass
class AbsentTeacher:
    teacher: None 
    length: str
    date: str
    note: str

    def __str__(self):
        return f"{self.first} {self.last} {self.length} {self.date} {self.note}"

@dataclass
class SchoologyCreds:
    keys: dict[SchoolName: str, SchoolName: str]
    secrets: dict[SchoolName: str, SchoolName: str]

class RawUpdate(BaseModel):
    poster: str
    content: list[str]
    columns: int = None
#
# SESSION AND TOKEN OBJECTS
#



