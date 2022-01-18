import sched
from typing import List, Literal, Optional
from uuid import UUID
from pydantic import BaseModel, validator
from dataStructs import *



class UserBase(BaseModel):
    first: str = None
    last: str = None
    school: SchoolName = None
    grade: Literal[9, 10, 11, 12] = None

    def __str__(self) -> str:
        return f"{self.first} {self.last}"
    
    def __hash__(self):
        return hash(str(self.number))

class UserCreate(UserBase):
    gid: str = None

class TeacherCreate(BaseModel):
    first: str = None
    last: str = None
    school: SchoolName = None

class TeacherReturn(TeacherCreate):
    tid: str = None

    class Config:
        orm_mode = True

class Schedule(BaseModel):
    A: List[TeacherReturn] = None
    ADV: List[TeacherReturn] = None
    B: List[TeacherReturn] = None
    C: List[TeacherReturn] = None 
    D: List[TeacherReturn] = None
    E: List[TeacherReturn] = None
    F: List[TeacherReturn] = None
    G: List[TeacherReturn] = None 

    @staticmethod
    def scheduleFromList(classes: list):
        schedule = Schedule()
        for cls in classes:
            current = getattr(schedule, cls.block)
            if current != None and current != NotPresent.TRUE:
                current.append(cls.teacher)
                setattr(schedule, cls.block, current)
            else:
                setattr(schedule, cls.block, [cls.teacher])
        return schedule

class Class(BaseModel):
    tid: str = None
    block: SchoolBlock = None
    uid: str = None

    class Config:
        orm_mode = True

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
    schedule: Schedule | List[Class] = [] 

    class Config:
        orm_mode = True

class UserInfo(BaseModel):
    profile: UserBase
    schedule: Schedule


class SessionCreate(BaseModel):
    uid: str

    @validator('uid')
    def checkUIDLength(cls, v):
        try:
            UUID(v)
            return v
        except:
            raise ValueError('Invalid UID.')

class SessionReturn(SessionCreate):
    sid: str = None
    last_accessed: int = None

    @validator('sid')
    def checkSIDLength(cls, v):
        if len(v) != 16:
            raise ValueError('SID Must be 17 characters long.')
        return v

class GToken(BaseModel):
    gToken: str
    def __str__(self):
        return self.gToken

class SessionCredentials(BaseModel):
    token: str | None = None
    refresh: str | None = None