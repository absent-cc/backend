from datetime import date, datetime
from enum import Enum
from dataclasses import dataclass
from typing import List, Literal, Set, Tuple
from collections import UserString
from uuid import UUID
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

class ClassTeachers(set[Teacher]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def __str__(self) -> str:
        return ", ".join(str(t) for t in self)
    def __repr__(self) -> str:
        return ", ".join(str(t) for t in self)

@dataclass
class AbsentTeacher:
    teacher: Teacher 
    length: str
    date: str
    note: str

    def __str__(self):
        return f"{self.first} {self.last} {self.length} {self.date} {self.note}"

# @dataclass
# class Schedule(dict):
#     def __init__(self,  
#                         A: ClassTeachers = None, 
#                         ADV: ClassTeachers = None,
#                         B: ClassTeachers = None,
#                         C: ClassTeachers = None, 
#                         D: ClassTeachers = None, 
#                         E: ClassTeachers = None, 
#                         F: ClassTeachers = None, 
#                         G: ClassTeachers = None):
#         self.schedule = {
#             SchoolBlock.A: A,
#             SchoolBlock.ADV: ADV,
#             SchoolBlock.B: B,
#             SchoolBlock.C: C,
#             SchoolBlock.D: D,
#             SchoolBlock.E: E,
#             SchoolBlock.F: F,
#             SchoolBlock.G: G
#         }
    
#     def __str__(self):
#         return f"""A: {self.schedule[SchoolBlock.A]}
#                     ADVISORY: {self.schedule[SchoolBlock.ADV]},
#                     B: {self.schedule[SchoolBlock.B]},
#                     C: {self.schedule[SchoolBlock.C]},
#                     D: {self.schedule[SchoolBlock.D]},
#                     E: {self.schedule[SchoolBlock.E]},
#                     F: {self.schedule[SchoolBlock.F]},
#                     G: {self.schedule[SchoolBlock.G]}"""
    
#     def __iter__(self):
#         yield from self.schedule.keys()

#     def __getitem__(self, key):
#         return self.schedule[key]
    
#     def __setitem__(self, key, value):
#         self.schedule[key] = value

#     def __delitem__(self, key):
#         del self.schedule[key]

#     def keys(self):
#         return self.schedule.keys()
    
#     def values(self):
#         return self.schedule.values()
    
#     def __contains__(self, item):
#         return item in self.schedule.keys()

#     def __hash__(self):
#         return hash(str(self))

@dataclass
class SchoologyCreds:
    keys: dict[SchoolName: str, SchoolName: str]
    secrets: dict[SchoolName: str, SchoolName: str]

#
# SESSION AND TOKEN OBJECTS
#

class Session(BaseModel):
    cid: str 
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
    token: str

