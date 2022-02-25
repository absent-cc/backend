from typing import List, Literal, Optional, Tuple, Union
from uuid import UUID
from pydantic import BaseModel, validator
from ..dataTypes import structs
from datetime import datetime, date

from ..database.database import Base

class UserBase(BaseModel):
    first: str = None
    last: str = None
    school: structs.SchoolName = None
    grade: Literal[9, 10, 11, 12] = None

    def __str__(self) -> str:
        return f"{self.first} {self.last}"
    
    def __hash__(self):
        return hash(str(self.number))

class UserCreate(UserBase):
    gid: str = None

class TeacherBase(BaseModel):
    first: str = None
    last: str = None

    def __repr__(self) -> str:
        return f"{self.first} {self.last}"

class TeacherCreate(TeacherBase):
    school: structs.SchoolName = None

    def __repr__(self) -> str:
        return f"{self.first} {self.last}"

class TeacherReturn(TeacherCreate):
    tid: str = None

    class Config:
        orm_mode = True

class Schedule(BaseModel):
    A: List[TeacherBase] = None
    ADVISORY: List[TeacherBase] = None
    B: List[TeacherBase] = None
    C: List[TeacherBase] = None
    D: List[TeacherBase] = None
    E: List[TeacherBase] = None
    F: List[TeacherBase] = None
    G: List[TeacherBase] = None
    EXTRA: List[TeacherBase] = None

class ScheduleReturn(BaseModel):
    A: List[TeacherReturn] = None
    ADVISORY: List[TeacherReturn] = None
    B: List[TeacherReturn] = None
    C: List[TeacherReturn] = None
    D: List[TeacherReturn] = None
    E: List[TeacherReturn] = None
    F: List[TeacherReturn] = None
    G: List[TeacherReturn] = None
    EXTRA: List[TeacherReturn] = None

    class Config:
        orm_mode = True

    @staticmethod
    def scheduleFromList(classes: list):
        schedule = ScheduleReturn()
        for cls in classes:
            current = getattr(schedule, cls.block)
            if current != None:
                current.append(TeacherReturn.from_orm(cls.teacher))
                setattr(schedule, cls.block, current)
            else:
                setattr(schedule, cls.block, [TeacherReturn.from_orm(cls.teacher)])
        return schedule

class Class(BaseModel):
    tid: str = None
    block: structs.SchoolBlock = None
    uid: str = None

    class Config:
        orm_mode = True

    def __repr__(self) -> str:
        return f"tid: {self.tid} Block: {self.block} uid: {self.uid}"
    
    # @staticmethod
    # def listFromSchedule(schedule: Schedule, uid: str):
    #     clsList = []
    #     for block in schedule:
    #         for _ in block[1]:
    #             clsList.append(Class(block=ReverseBlockMapper()[block[0]], uid=uid))
    #     return clsList

class TeacherFull(TeacherReturn):
    schedule: List[Class] = []
    
    class Config:
        orm_mode = True

class UserReturn(UserCreate):
    uid: str = None
    schedule: Union[ScheduleReturn, List[Class]] = []

    class Config:
        orm_mode = True

class SessionCreate(BaseModel):
    uid: Optional[str] = None
    @validator('uid')
    def checkUIDLength(cls, v):
        try:
            UUID(v)
            return v
        except:
            raise ValueError('Invalid UID.')

class SessionReturn(SessionCreate):
    sid: Optional[str] = None
    last_accessed: Optional[datetime] = None

    @validator('sid')
    def checkSIDLength(cls, v):
        if len(v) != 16:
            raise ValueError('SID Must be 17 characters long.')
        return v
    class Config:
        orm_mode = True

class Token(BaseModel):
    token: str

class UserInfo(BaseModel):
    profile: UserBase
    schedule: Schedule
    fcm: Token

class UserInfoReturn(BaseModel):
    profile: UserBase
    schedule: ScheduleReturn
    fcm: Token

class SessionCredentials(BaseModel):
    token: Optional[str] = None
    refresh: Optional[str] = None
    onboarded: Optional[bool] = None

class AbsenceBase(BaseModel):
    length: Optional[str] = None
    note: Optional[str] = None

class AbsenceCreate(AbsenceBase):
    teacher: TeacherCreate
    date: date

    def __repr__(self) -> str:
        return super().__repr__()

class AbsenceReturn(AbsenceBase):
    teacher: TeacherReturn
    date: date

class CanceledClassCreate(Class):
    date: date

    def __repr__(self) -> str:
        return super().__repr__()

class PartialName(BaseModel):
    name: str 
    school: str

    @validator('name')
    def checkPartialName(cls, v):
        if (len(v)) < 3:
            raise ValueError('Phrase too short.')
        return v
        
    @validator('school')
    def checkSchoolName(cls, v):
        if (v != "NNHS") and (v != "NSHS"):
            raise ValueError('Invalid school.')
        return v

class SessionList(BaseModel):
    sessions: List[SessionReturn]

class AbsenceList(BaseModel):
    absences: Tuple[AbsenceReturn]

class AutoComplete(BaseModel):
    suggestions: list

class TeacherValid(BaseModel):
    value: bool
    formatted: str = None
    suggestions: List[str] = None

class ClassList(BaseModel):
    classes: List[structs.SchoolBlock] = None

class Analytics(BaseModel):
    userCount: int
    totalAbsences: int

class Bool(BaseModel):
    success: bool

class Badges(BaseModel):
    schemaVersion: int = 1
    label: str
    message: str
    color: str = "#FF793F"
    labelColor: str = "grey"
    isError: bool = False
    # namedLogo: str = None
    # logoSvg: str = None
    # logoColor: str = None
    # logoWidth: str = None
    # logoPostion: str = None
    # style: str = "flat"
    # cacheSeconds: int = 300

class UserCountBadge(Badges):
    label = "Active Users"
    message: str

class AbsencesBadge(Badges):
    label = "Absences Reported"
    message: str

class ClassCountBadge(Badges):
    label = "Classes Serving"
    message: str

class ClassCanceledBadge(Badges):
    label = "Classes Canceled"
    message: str
class Date(BaseModel):
    date: date