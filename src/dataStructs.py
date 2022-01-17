from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Literal, Set
from uuid import UUID
from pydantic import BaseModel, ValidationError, validator

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

class SchoolBlock(str, Enum):
    A: str = "A"
    ADV: str = "ADVISORY"
    B: str = "B"
    C: str = "C"
    D: str = "D"
    E: str = "E"
    F: str = "F"
    G: str = "G"

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

class Student(BaseModel):
    uid: UUID = None
    gid:  int = None
    first: str = None
    last: str = None
    school: SchoolName = None
    grade: Literal["9", "10", "11", "12"] = None

    def __str__(self) -> str:
        return f"{self.first} {self.last}"
    
    def __hash__(self):
        return hash(str(self.number))

class Teacher(BaseModel):
    first: str
    last: str
    school: SchoolName 
    tid: int = None
    
    def __hash__(self):
        primaryKey = self.first + self.last + str(self.school)
        return hash(primaryKey)
    def __str__(self) -> str:
        return f"{self.first} {self.last}"
    def __repr__(self) -> str:
        return f"{self.first} {self.last}"
    def __eq__ (self, other):
        if type(other) is not Teacher: return False
        return self.first == other.first and self.last == other.last and self.school == other.school

@dataclass
class AbsentTeacher:
    teacher: Teacher 
    length: str
    date: str
    note: str

    def __str__(self):
        return f"{self.first} {self.last} {self.length} {self.date} {self.note}"

@dataclass
class SchoologyCreds:
    keys: dict[SchoolName: str, SchoolName: str]
    secrets: dict[SchoolName: str, SchoolName: str]

#
# SESSION AND TOKEN OBJECTS
#

class ClientID(BaseModel):
    token: str
    uuid: UUID
    
    def __str__(self):
        return self.token + '.' + str(self.uuid)
    
    # LENGTH = 17
    # def __init__(self, *args, **kwargs):
    #     split = args[0].split('.')
    #     if len(split[0]) != self.LENGTH:
    #         raise ValueError("Token must be 17 characters long")
    #     try:
    #         split = args[0].split('.')
    #         UUID(split[1], version=4)
    #     except:
    #         raise ValueError("Invalid UUID segment.")
        
    #     super().__init__(*args, **kwargs)

    @validator('token')
    def checkTokenLength(cls, v):
        if len(v) != 16:
            raise ValueError('Must be 17 characters long.')
        return v

class Session(BaseModel):
    cid: ClientID 
    startTime: datetime | None = None
    validity: bool = True

class GToken(BaseModel):
    gToken: str
    def __str__(self):
        return self.gToken

#
# SCHEMAS
#

class Schedule(BaseModel):
    A: None | List[Teacher] = NotPresent.TRUE
    ADV: None | List[Teacher] = NotPresent.TRUE
    B: None | List[Teacher] = NotPresent.TRUE
    C: None | List[Teacher] = NotPresent.TRUE
    D: None | List[Teacher] = NotPresent.TRUE
    E: None | List[Teacher] = NotPresent.TRUE
    F: None | List[Teacher] = NotPresent.TRUE
    G: None | List[Teacher] = NotPresent.TRUE

class Profile(BaseModel):
    first: None | str = NotPresent.TRUE
    last: None | str = NotPresent.TRUE
    school: None | SchoolName = NotPresent.TRUE
    grade: None | Literal["9", "10", "11", "12"] = NotPresent.TRUE

    def __str__(self) -> str:
        return f"{self.first} {self.last}"
    
    def __hash__(self):
        return hash(str(self.number))

class BasicInfo(BaseModel):
    profile: Profile | None = None
    schedule: Schedule | None = None

class SessionCredentials(BaseModel):
    token: str | None = None
    refresh: str | None = None

