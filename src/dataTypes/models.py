from email.policy import default
from sqlalchemy import (
    Column,
    ForeignKey,
    UniqueConstraint,
    TIMESTAMP,
    Date,
    String,
    Boolean,
    Enum,
    PickleType,
    Text,
    DateTime,
    Integer,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import relationship, validates

from . import structs

if "alembic.env" in __name__:
    from ..database.database import Base  # CHANGE THIS TO ..database for ALEMBIC
else:
    from ..database.database import Base  # CHANGE THIS TO ..database for ALEMBIC


class User(Base):
    __tablename__ = "users"
    uid = Column(String(36), primary_key=True)
    gid = Column(String(255), unique=True)
    first = Column(String(255))
    last = Column(String(255))
    school = Column(Enum(structs.SchoolName))
    grade = Column(Enum(structs.Grade))

    schedule = relationship("Class", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")
    settings = relationship("UserSettings", back_populates="user")

    def __str__(self) -> str:
        return f"{self.first} {self.last} ({self.school} {self.grade})"


class Teacher(Base):
    __tablename__ = "teachers"
    tid = Column(String(8), primary_key=True)
    first = Column(String(255, collation="nocase"))
    last = Column(String(255, collation="nocase"))
    school = Column(Enum(structs.SchoolName))

    classes = relationship("Class", back_populates="teacher")
    __table_args__ = (UniqueConstraint("first", "last", "school"),)

    def __str__(self) -> str:
        return f"{self.first} {self.last} ({self.school})"


class UserSession(Base):
    __tablename__ = "sessions"
    sid = Column(String(16), primary_key=True)
    uid = Column(String(36), ForeignKey(User.uid, ondelete="CASCADE"))
    last_accessed = Column(TIMESTAMP)
    fcm_token = Column(String(255))
    fcm_timestamp = Column(TIMESTAMP)

    user = relationship("User")
    __table_args__ = (UniqueConstraint("sid", "uid"),)


class Class(Base):
    __tablename__ = "classes"
    cid = Column(String(8), primary_key=True)
    tid = Column(String(8), ForeignKey(Teacher.tid, ondelete="CASCADE"))
    block = Column(Enum(structs.SchoolBlock))
    uid = Column(String(36), ForeignKey(User.uid, ondelete="CASCADE"))

    teacher = relationship("Teacher")
    user = relationship("User")
    __table_args__ = (UniqueConstraint("tid", "block", "uid"),)

    def __str__(self) -> str:
        return f"{self.block} {self.teacher} {self.user}"


class Absence(Base):
    __tablename__ = "absences"
    tid = Column(
        String(8), ForeignKey(Teacher.tid, ondelete="CASCADE"), primary_key=True
    )
    length = Column(String(255))
    note = Column(String(255))
    date = Column(Date, primary_key=True)

    teacher = relationship("Teacher")


class UserSettings(Base):
    __tablename__ = "settings"
    uid = Column(String(36), ForeignKey(User.uid, ondelete="CASCADE"), primary_key=True)
    showFreeAsAbsent = Column(Boolean)
    notify = Column(Boolean)
    notifyWhenNone = Column(Boolean)

    user = relationship("User")


class SpecialDays(Base):
    __tablename__ = "special_days"
    spid = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    name = Column(String(255))
    schedule = Column(PickleType)
    note = Column(String(255))
    school = Column(Enum(structs.SchoolName))

    @validates("schedule")
    def validate_schedule_type(self, key, value):
        if type(value) != structs.ScheduleWithTimes:
            raise ValueError("Schedule must be of type ScheduleWithTimes")
        return value

    def __str__(self) -> str:
        return f"{self.name} ({self.date}):\n\t{self.schedule}\n\tNote: {self.note}"


class Aliases(Base):
    __tablename__ = "aliases"
    alid = Column(String(8), primary_key=True)
    first = Column(String(255), primary_key=True)
    last = Column(String(255), primary_key=True)
    tid = Column(String(36), ForeignKey(Teacher.tid, ondelete="CASCADE"))

    def __str__(self) -> str:
        return f"{self.first} {self.last} ({self.tid})"

    # teacher = relationship("Teacher", back_populates="aliases")


class Announcements(Base):
    __tablename__ = "announcements"
    anid = Column(String(8), primary_key=True)
    title = Column(String(255))
    content = Column(Text)  # Markdown variably sized string
    date = Column(Date)
    school = Column(Enum(structs.SchoolName), nullable=True)
    lastUpdate = Column(DateTime, nullable=True)

    def __str__(self) -> str:
        lines = "---------------------\n"
        header = f"Announcement:\n\tID: {self.anid}\n\tTitle: {self.title}\n\tDate: {self.date}\n\tSchool: {self.school}\n\tLast Update: {self.lastUpdate}\n\tContent:"
        return lines + header + "\n\t" + self.content + "\n" + lines
