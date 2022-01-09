from datetime import date, datetime
from enum import Enum
from dataclasses import dataclass
from typing import Set
from collections import UserString
from uuid import UUID
from pydantic import BaseModel

class SchoolNameMapper(dict):
    def __init__(self):
        super().__init__()
        self.update({
            "NSHS": SchoolName.NEWTON_SOUTH,
            "NNHS": SchoolName.NEWTON_NORTH
        })

class ReverseSchoolNameMapper(dict):
    def __init__(self):
        super().__init__()
        self.update({
            SchoolName.NEWTON_SOUTH: "NSHS",
            SchoolName.NEWTON_NORTH: "NNHS"
        })

class SchoolName(Enum):
    NEWTON_SOUTH = "NSHS"
    NEWTON_NORTH = "NNHS"

    def __str__(self) -> str:
        if self == SchoolName.NEWTON_SOUTH:
            return "NSHS"
        elif self == SchoolName.NEWTON_NORTH:
            return "NNHS"
        else:
            return "Unknown School"

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
            "G": SchoolBlock.G
        })

class SchoolBlock(Enum):
    A = "A"
    ADV = "ADVISORY"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"

    def __str__(self) -> str:
        mapper = BlockMapper()
        return mapper[self]
        
    def __repr__(self) -> str:
        mapper = BlockMapper()
        return mapper[self]

@dataclass
class Student:
    uuid: UUID
    subject: str
    first: str
    last: str
    school: SchoolName
    grade: int

    def __str__(self) -> str:
        return f"{self.first} {self.last}"
    
    def __hash__(self):
        return hash(str(self.number))

@dataclass
class Teacher:
    first: str
    last: str
    school: SchoolName
    id: int = None

    def __str__(self) -> str:
        return f"{self.first} {self.last}"
    def __hash__(self):
        primaryKey = self.first + self.last + str(self.school)
        return hash(primaryKey)
    def __repr__(self) -> str:
        return f"{self.first} {self.last}"
    def __eq__ (self, other):
        if type(other) is not Teacher: return False
        return self.first == other.first and self.last == other.last and self.school == other.school

class ClassTeachers(Set[Teacher]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def __str__(self) -> str:
        return ", ".join(str(t) for t in self)
    def __repr__(self) -> str:
        return ", ".join(str(t) for t in self)

@dataclass
class Schedule(dict):
    def __init__(self,  
                        A: ClassTeachers = None, 
                        ADV: ClassTeachers = None,
                        B: ClassTeachers = None,
                        C: ClassTeachers = None, 
                        D: ClassTeachers = None, 
                        E: ClassTeachers = None, 
                        F: ClassTeachers = None, 
                        G: ClassTeachers = None):
        self.schedule = {
            SchoolBlock.A: A,
            SchoolBlock.ADV: ADV,
            SchoolBlock.B: B,
            SchoolBlock.C: C,
            SchoolBlock.D: D,
            SchoolBlock.E: E,
            SchoolBlock.F: F,
            SchoolBlock.G: G
        }
    
    def __str__(self):
        return f"""A: {self.schedule[SchoolBlock.A]}
                    ADVISORY: {self.schedule[SchoolBlock.ADV]},
                    B: {self.schedule[SchoolBlock.B]},
                    C: {self.schedule[SchoolBlock.C]},
                    D: {self.schedule[SchoolBlock.D]},
                    E: {self.schedule[SchoolBlock.E]},
                    F: {self.schedule[SchoolBlock.F]},
                    G: {self.schedule[SchoolBlock.G]}"""
    
    def __iter__(self):
        yield from self.schedule.keys()

    def __getitem__(self, key):
        return self.schedule[key]
    
    def __setitem__(self, key, value):
        self.schedule[key] = value

    def __delitem__(self, key):
        del self.schedule[key]
    
    def keys(self):
        return self.schedule.keys()
    
    def values(self):
        return self.schedule.values()
    
    def __contains__(self, item):
        return item in self.schedule.keys()

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

# API Stuff

class Token(UserString):
    LENGTH = 86
    def __init__(self, *args, **kwargs):
        if len(args[0]) != self.LENGTH:
            raise ValueError("Token must be 86 characters long")
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.data

class ClientID(UserString):
    LENGTH = 53
    def __init__(self, *args, **kwargs):
        if len(args[0]) != self.LENGTH:
            raise ValueError("ClientID must be 53 characters long")
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.data

@dataclass
class Session():
    uuid: UUID
    clientID: ClientID
    token: Token
    start_time: datetime
    validity: bool = True
    id: int = None

class IDToken(BaseModel):
    idToken: str

    def __str__(self):
        return self.idToken


    