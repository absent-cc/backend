from ast import alias
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
    DateTime
)
from sqlalchemy.orm import relationship, validates

from . import structs

if "alembic.env" in __name__:
    from ..database.database import Base  # CHANGE THIS TO ..database for ALEMBIC
else:
    from ..database.database import Base  # CHANGE THIS TO ..database for ALEMBIC


# Table for everything User related
class User(Base):
    __tablename__ = "users"
    uid = Column(String(36), primary_key=True)
    gid = Column(String(255), unique=True)
    first = Column(String(255))
    last = Column(String(255))
    school = Column(Enum(structs.SchoolName))
    grade = Column(Enum(structs.Grade))

    schedule = relationship("Classes", back_populates="user")
    sessions = relationship("UserSessions", back_populates="user")
    settings = relationship("UserSettings", back_populates="user")
    social = relationship("UserSocial", back_populates="user")
    friends = relationship("Friends", back_populates="user", foreign_keys="Friends.uid")

    def __str__(self) -> str:
        return f"{self.first} {self.last} ({self.school} {self.grade})"

# Table for everything Teacher related
class Teacher(Base):
    __tablename__ = "teachers"
    tid = Column(String(8), primary_key=True)
    first = Column(String(255, collation="nocase"))
    last = Column(String(255, collation="nocase"))
    school = Column(Enum(structs.SchoolName))
    source = Column(Enum(structs.TeacherReportSource))

    classes = relationship("Classes", back_populates="teacher")
    aliases = relationship("Aliases", back_populates="teacher")
    absences = relationship("Absences", back_populates="teacher")

    __table_args__ = (UniqueConstraint("first", "last", "school"),)

    def __str__(self) -> str:
        return f"{self.first} {self.last} ({self.school})"

# Table for User Sessions
# This is a one-to-many relationship with User
# (1 User - > X UserSession)
# Each additional session is a new login on a device
class UserSessions(Base):
    __tablename__ = "sessions"
    sid = Column(String(16), primary_key=True)
    uid = Column(String(36), ForeignKey(User.uid, ondelete="CASCADE"))
    last_accessed = Column(TIMESTAMP)
    fcm_token = Column(String(255))
    fcm_timestamp = Column(TIMESTAMP)

    user = relationship("User")

    __table_args__ = (UniqueConstraint("sid", "uid"),)


# Table listing Classes
# Links a User to a Teacher through a Class entry
# 1 to Many relationship with User and Teacher
# (1 User - > X Class)
# (1 Teacher - > X Class)
class Classes(Base):
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


class Absences(Base):
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
    date = Column(Date, primary_key=True)
    name = Column(String(255))
    schedule = Column(PickleType)
    note = Column(String(255))

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
    
    teacher = relationship("Teacher")
   
    def __str__(self) -> str:
        return f"{self.first} {self.last} ({self.tid})"

class Announcements(Base):
    __tablename__ = "announcements"
    anid = Column(String(8), primary_key=True)
    title = Column(String(255))
    content = Column(Text) # Markdown variably sized string
    date = Column(Date)
    school = Column(Enum(structs.SchoolName), nullable=True)
    lastUpdate = Column(DateTime, nullable=True)

    def __str__(self) -> str:
        lines="---------------------\n"
        header = f"Announcement:\n\tID: {self.anid}\n\tTitle: {self.title}\n\tDate: {self.date}\n\tSchool: {self.school}\n\tLast Update: {self.lastUpdate}\n\tContent:"
        return lines + header + "\n\t" + self.content + "\n" + lines


class Friends(Base):
    __tablename__ = "friends"
    uid = Column(String(36), ForeignKey(User.uid, ondelete="CASCADE"), primary_key=True)
    fid = Column(String(36), ForeignKey(User.uid, ondelete="CASCADE"), primary_key=True)
    status = Column(Enum(structs.FriendshipStatus))
    date = Column(Date, primary_key=True)

    __table_args__ = (UniqueConstraint("uid", "fid"),)

    user = relationship("User", foreign_keys=[uid])
    friend = relationship("User", foreign_keys=[fid])

    def __str__(self) -> str:
        return f"{self.user} --({self.status})--> {self.friend} | {self.date}"

class UserSocial(Base):
    __tablename__ = "social"
    uid = Column(String(36), ForeignKey(User.uid, ondelete="CASCADE"), primary_key=True)
    instagram = Column(String(255))
    snapchat = Column(String(255))
    messenger = Column(String(255))
    phone = Column(String(255))
    # Remeber if you make changes to the columns here, you make changes in schemas.py as well!

    __table_args__ = (UniqueConstraint("uid"),)
    user = relationship("User")