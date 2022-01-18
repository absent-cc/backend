from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database.database import Base

class User(Base):
    __tablename__ = "users"
    uid = Column(String, primary_key=True)
    gid = Column(String, unique=True)
    first = Column(String)
    last = Column(String)
    school = Column(String)
    grade = Column(Integer)

    schedule = relationship("Class", back_populates="user")
    sessions = relationship("UserSession")

class Class(Base):
    __tablename__ = "classes"
    tid = Column(Integer, ForeignKey("teachers.tid"), primary_key=True)
    block = Column(String, primary_key=True)
    uid = Column(String, ForeignKey("users.uid"), primary_key=True)

    teacher = relationship("Teacher")
    user = relationship("User")

class Teacher(Base):
    __tablename__ = "teachers"
    tid = Column(String)
    first = Column(String, primary_key=True)
    last = Column(String, primary_key=True)
    school = Column(String, primary_key=True)

    schedule = relationship("Class", back_populates="teacher")

class UserSession(Base):
    __tablename__ = "sessions"
    sid = Column(String, primary_key=True)
    uid = Column(String, ForeignKey("users.uid"), primary_key=True)
    last_accessed = Column(Integer)