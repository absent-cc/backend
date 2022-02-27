from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint, TIMESTAMP, Text, collate
from sqlalchemy.orm import relationship
from citext import CIText

if "alembic.env" in __name__:
    from ..database.database import Base # CHANGE THIS TO ..database for ALEMBIC
else:
    from ..database.database import Base # CHANGE THIS TO ..database for ALEMBIC

class User(Base):
    __tablename__ = "users"
    uid = Column(String(36), primary_key=True)
    gid = Column(String(255), unique=True)
    first = Column(Text(255))
    last = Column(Text(255))
    school = Column(String(4))
    grade = Column(Integer)

    schedule = relationship("Class", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")

    caseInsensitiveFirst = collate('first', 'NOCASE')
    caseInsensitiveLast = collate('last', 'NOCASE')

class Teacher(Base):
    __tablename__ = "teachers"
    tid = Column(String(8), primary_key=True)
    first = Column(Text(255))
    last = Column(Text(255))
    school = Column(String(4))

    schedule = relationship("Class", back_populates="teacher")
    __table_args__ = (UniqueConstraint('first', 'last', 'school'),)
    
    caseInsensitiveFirst = collate('first', 'NOCASE')
    caseInsensitiveLast = collate('last', 'NOCASE')
class UserSession(Base):
    __tablename__ = "sessions"
    sid = Column(String(16), primary_key=True)
    uid = Column(String(36), ForeignKey(User.uid, ondelete='CASCADE'))
    last_accessed = Column(TIMESTAMP)
    fcm_token = Column(String(255))
    fcm_timestamp = Column(TIMESTAMP)

    user = relationship("User")
    __table_args__ = (UniqueConstraint('sid', 'uid'),)
class Class(Base):
    __tablename__ = "classes"
    cid = Column(String(8), primary_key=True)
    tid = Column(String(8), ForeignKey(Teacher.tid, ondelete='CASCADE'))
    block = Column(String(8))
    uid = Column(String(36), ForeignKey(User.uid, ondelete='CASCADE'))

    teacher = relationship("Teacher")
    user = relationship("User")
    __table_args__ = (UniqueConstraint('tid', 'block', 'uid'),)

class Absence(Base):
    __tablename__ = "absences"
    tid = Column(String(8), ForeignKey(Teacher.tid, ondelete='CASCADE'), primary_key=True)
    length = Column(String(255))
    note = Column(String(255))
    date = Column(TIMESTAMP, primary_key=True)

    teacher = relationship("Teacher")

class CancelledClass(Base):
    __tablename__ = "cancelled"
    index = Column(Integer, primary_key=True, autoincrement=True)
    cid = Column(String(8), ForeignKey(Class.cid, ondelete='CASCADE'),)
    date = Column(TIMESTAMP)
    
    parent = relationship("Class")
    __table_args__ = (UniqueConstraint('cid', 'date'),)