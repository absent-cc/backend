from datetime import datetime, date
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, validator

from ..dataTypes import structs


class UserSettings(BaseModel):
    showFreeAsAbsent: bool = False
    notify: bool = True
    notifyWhenNone: bool = True

    class Config:
        orm_mode = True


class UserSettingsCreate(UserSettings):
    uid: UUID


class UserBase(BaseModel):
    first: Optional[str] = None
    last: Optional[str] = None
    school: Optional[structs.SchoolName] = None
    grade: Optional[structs.Grade] = None

    def __str__(self) -> str:
        return f"{self.first} {self.last} ({self.school} {self.grade})"

    def __hash__(self):
        return hash(str(self.number))


class UserCreate(UserBase):
    gid: Optional[str] = None


class TeacherBase(BaseModel):
    first: Optional[str] = None
    last: Optional[str] = None

    def __repr__(self) -> str:
        return f"{self.first} {self.last}"

    def __str__(self) -> str:
        return self.__repr__()


class TeacherCreate(TeacherBase):
    school: Optional[structs.SchoolName] = None

    def __repr__(self) -> str:
        return f"{self.first} {self.last}"


class TeacherReturn(TeacherCreate):
    tid: str = None

    def __repr__(self) -> str:
        return f"{self.first} {self.last} {self.tid} {self.school}"

    class Config:
        orm_mode = True


class Schedule(BaseModel):
    A: Optional[List[TeacherBase]] = None
    ADVISORY: Optional[List[TeacherBase]] = None
    B: Optional[List[TeacherBase]] = None
    C: Optional[List[TeacherBase]] = None
    D: Optional[List[TeacherBase]] = None
    E: Optional[List[TeacherBase]] = None
    F: Optional[List[TeacherBase]] = None
    G: Optional[List[TeacherBase]] = None
    EXTRA: Optional[List[TeacherBase]] = None

    class Config:
        orm_mode = True

    def __str__(self) -> str:
        return f"A: {self.A}\nADV: {self.ADVISORY}\nB: {self.B}\nC: {self.C}\nD: {self.D}\nE: {self.E}\nF: {self.F}\nG: {self.G}\nEXTRA: {self.EXTRA}"


class ScheduleReturn(BaseModel):
    A: Optional[List[TeacherReturn]] = None
    ADVISORY: Optional[List[TeacherReturn]] = None
    B: Optional[List[TeacherReturn]] = None
    C: Optional[List[TeacherReturn]] = None
    D: Optional[List[TeacherReturn]] = None
    E: Optional[List[TeacherReturn]] = None
    F: Optional[List[TeacherReturn]] = None
    G: Optional[List[TeacherReturn]] = None
    EXTRA: Optional[List[TeacherReturn]] = None

    class Config:
        orm_mode = True

    @staticmethod
    def scheduleFromList(classes: list):
        schedule = ScheduleReturn()
        for cls in classes:
            current = getattr(schedule, cls.block)
            if current is not None:
                current.append(TeacherReturn.from_orm(cls.teacher))
                setattr(schedule, cls.block, current)
            else:
                setattr(schedule, cls.block, [TeacherReturn.from_orm(cls.teacher)])
        return schedule


class Class(BaseModel):
    tid: Optional[str] = None
    block: Optional[structs.SchoolBlock] = None
    uid: Optional[str] = None

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
    uid: Optional[str] = None
    schedule: Union[ScheduleReturn, List[Class]] = []

    class Config:
        orm_mode = True


class UserProfile(UserCreate):
    uid: Optional[str] = None

    class Config:
        orm_mode = True


class UserSchedule(UserCreate):
    uid: Optional[str] = None

    class Config:
        orm_mode = True


class SessionCreate(BaseModel):
    uid: Optional[str] = None

    @validator("uid")
    def checkUIDLength(cls, v):
        try:
            UUID(v)
            return v
        except:
            raise ValueError("Invalid UID.")


class SessionReturn(SessionCreate):
    sid: Optional[str] = None
    last_accessed: Optional[datetime] = None

    @validator("sid")
    def checkSIDLength(cls, v):
        if len(v) != 16:
            raise ValueError("SID Must be 17 characters long.")
        return v

    class Config:
        orm_mode = True


class Token(BaseModel):
    token: str


class UserInfoBase(BaseModel):
    settings: Optional[UserSettings] = None


class UserInfoUpdate(UserInfoBase):
    schedule: Optional[Schedule] = None
    profile: Optional[UserBase] = None
    fcm: Optional[Token] = None


class UserInfoReturn(UserInfoBase):
    schedule: Optional[ScheduleReturn] = None
    profile: Optional[UserProfile] = None
    onboarded: Optional[bool] = None


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


class PartialName(BaseModel):
    name: str
    school: structs.SchoolName

    @validator("name")
    def checkPartialName(cls, v):
        if (len(v)) < 3:
            raise ValueError("Phrase too short.")
        return v


class SessionList(BaseModel):
    sessions: List[SessionReturn]


class AbsenceList(BaseModel):
    absences: List[AbsenceReturn]
    date: date


class ManualAbsencesReturn(BaseModel):
    absences: List[AbsenceList]
    success: bool


class AutoComplete(BaseModel):
    suggestions: list


class TeacherValid(BaseModel):
    value: bool
    formatted: Optional[str] = None
    suggestions: Optional[List[str]] = None


class ClassList(BaseModel):
    classes: Optional[List[structs.SchoolBlock]] = None


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
    label = "Free Blocks Recorded"
    message: str


class Date(BaseModel):
    date: date


class SchoolDay(BaseModel):
    date: date
    name: str
    schedule: structs.ScheduleWithTimes
    note: Optional[str] = None
    special: bool
    school: Optional[structs.SchoolName] = None

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

        # @staticmethod
        # def schema_extra(schema: Dict[str, Any], model: Type['SchoolDay']) -> None:
        #     for prop in schema.get('properties', {}).values():
        #         prop.pop('title', None)

        schema_extra = {
            "example": {
                "date": "2020-01-01",
                "name": "New Years Day",
                "schedule": [
                    {
                        "block": "A",
                        "startTime": "09:00:00",
                        "endTime": "10:00:00",
                        "lunches": [
                            {
                                "lunch": "L1",
                                "startTime": "10:00:00",
                                "endTime": "11:00:00",
                            },
                        ],
                    },
                ],
                "note": "Happy New Years!",
                "special": True,
                "school": "NSHS",
            }
        }

    @validator("date")
    def checkDate(cls, v):
        if not isinstance(v, date):
            raise ValueError("Invalid date.")
        return v


class SpecialDay(SchoolDay):
    special = True


class NormalDay(SchoolDay):
    name = "Normal Day"
    note = "No special schedule"
    special = False


class AnnouncementBase(BaseModel):
    title: str
    content: str
    school: Optional[structs.SchoolName]
    date: Optional[date]

    class Config:
        orm_mode = True


class AnnouncementCreate(AnnouncementBase):
    anid: str

    class Config:
        orm_mode = True


class AnnouncementReturn(AnnouncementCreate):
    class Config:
        orm_mode = True


class AnnouncementUpdate(AnnouncementCreate):
    updateTime: datetime

    class Config:
        orm_mode = True


class TeacherAliasBase(BaseModel):
    first: str
    last: str
    school: structs.SchoolName

    class Config:
        orm_mode = True


class TeacherAliasCreate(TeacherAliasBase):
    actual_first: str
    actual_last: str
    actual_school: structs.SchoolName
    class Config:
        orm_mode = True
    
    def __str__(self) -> str:
        return f"{self.first} {self.last} -> {self.actual_first} {self.actual_last} ({self.school})"


class TeacherAliasReturn(TeacherAliasBase):
    alid: str
    tid: str

    class Config:
        orm_mode = True
