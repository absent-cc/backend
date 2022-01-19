from enum import auto
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from database.database import Base

class User(Base):
    __tablename__ = "users"
    uid = Column(String(36), primary_key=True)
    gid = Column(String(255), unique=True)
    first = Column(String(255))
    last = Column(String(255))
    school = Column(String(4))
    grade = Column(Integer)

    schedule = relationship("Class", back_populates="user")
    sessions = relationship("UserSession")
    __table_args__ = {'mysql_engine':'InnoDB'}

class Teacher(Base):
    __tablename__ = "teachers"
    tid = Column(String(16), primary_key=True)
    first = Column(String(255))
    last = Column(String(255))
    school = Column(String(4))

    schedule = relationship("Class", back_populates="teacher")
    __table_args__ = {'mysql_engine':'InnoDB'}
    
class UserSession(Base):
    __tablename__ = "sessions"
    sid = Column(String(16), primary_key=True)
    uid = Column(String(36), ForeignKey(User.uid, ondelete='CASCADE'), primary_key=True)
    last_accessed = Column(Integer)
    __table_args__ = {'mysql_engine':'InnoDB'}

class Class(Base):
    __tablename__ = "classes"
    tid = Column(String(16), ForeignKey(Teacher.tid, ondelete='CASCADE'), primary_key=True)
    block = Column(String(8), primary_key=True)
    uid = Column(String(36), ForeignKey(User.uid, ondelete='CASCADE'), primary_key=True)

    teacher = relationship("Teacher")
    user = relationship("User")
    __tableargs__ = {'mysql_engine':'InnoDB'}