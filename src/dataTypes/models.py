from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint, TIMESTAMP
from sqlalchemy.orm import relationship

if "alembic.env" in __name__:
    from ..database.database import Base # CHANGE THIS TO ..database for ALEMBIC
else:
    from ..database.database import Base # CHANGE THIS TO ..database for ALEMBIC
class User(Base):
    __tablename__ = "users"
    uid = Column(String(36), primary_key=True)
    gid = Column(String(255), unique=True)
    first = Column(String(255))
    last = Column(String(255))
    school = Column(String(4))
    grade = Column(Integer)

    schedule = relationship("Class", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")

class Teacher(Base):
    __tablename__ = "teachers"
    tid = Column(String(8), primary_key=True)
    first = Column(String(255))
    last = Column(String(255))
    school = Column(String(4))

    schedule = relationship("Class", back_populates="teacher")
    __table_args__ = (UniqueConstraint('first', 'last', 'school'),)
    
class UserSession(Base):
    __tablename__ = "sessions"
    sid = Column(String(16), primary_key=True)
    uid = Column(String(36), ForeignKey(User.uid, ondelete='CASCADE'), primary_key=True)
    last_accessed = Column(TIMESTAMP)
    fcm_token = Column(String(255))
    fcm_timestamp = Column(TIMESTAMP)

    user = relationship("User")

class Class(Base):
    __tablename__ = "classes"
    cid = Column(Integer, primary_key=True, autoincrement=True)
    tid = Column(String(8), ForeignKey(Teacher.tid, ondelete='CASCADE'), primary_key=True)
    block = Column(String(8), primary_key=True)
    uid = Column(String(36), ForeignKey(User.uid, ondelete='CASCADE'), primary_key=True)

    teacher = relationship("Teacher")
    user = relationship("User")

class Absence(Base):
    __tablename__ = "absences"
    tid = Column(String(8), ForeignKey(Teacher.tid, ondelete='CASCADE'), primary_key=True)
    note = Column(String(255))
    date = Column(TIMESTAMP, primary_key=True)

    teacher = relationship("Teacher")

class CanceledClass(Base):
    __tablename__ = "canceled"
    cls = Column(String(8), ForeignKey(Class.cid, ondelete='CASCADE'), primary_key=True)
    date = Column(TIMESTAMP, primary_key=True)

    cls = relationship("Class")