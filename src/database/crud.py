import time
from uuid import UUID, uuid4
from sqlalchemy import update
from sqlalchemy.orm import Session 
from . import models, schemas
from .database import SessionLocal, engine
from dataStructs import *
import secrets

class CRUD:
    def __init__(self):
        self.db = SessionLocal()

    def getUser(self, user: schemas.UserReturn):
        if user.uid != None:
            return self.db.query(models.User).filter(models.User.uid == user.uid).first()
        if user.gid != None:
            return self.db.query(models.User).filter(models.User.gid == user.gid).first()
        return None

    def getTeacher(self, teacher: schemas.TeacherReturn):
        if teacher.tid != None:
            return self.db.query(models.Teacher).filter(models.Teacher.tid == teacher.tid).first()
        return self.db.query(models.Teacher).filter(models.Teacher.first == teacher.first, models.Teacher.last == teacher.last, models.Teacher.school == teacher.school).first()

    def getSession(self, session: schemas.SessionReturn):
        if session.sid != None and session.uid != None:
            return self.db.query(models.UserSession).filter(models.UserSession.uid == session.uid, models.UserSession.sid == session.sid).first()
        raise ValueError("Missing SID, UID, or both.")

    def getClass(self, cls: schemas.Class):
        return self.db.query(models.Class).filter(models.Class.tid == cls.tid, models.Class.uid == cls.uid, models.Class.block == cls.block).first()

    def getClassesByUser(self, user: schemas.UserReturn):
        return self.db.query(models.Class).filter(models.Class.uid == user.uid).all()

    def addUser(self, user: schemas.UserCreate):
        uid = str(uuid4())
        userModel = models.User(uid=uid, **user.dict())
        self.db.add(userModel)
        self.db.commit()
        self.db.refresh(userModel)
        return userModel

    def addClass(self, newClass: schemas.Class):
        classModel = models.Class(**newClass.dict())
        self.db.add(classModel)
        self.db.commit()
        self.db.refresh(classModel)
        return classModel

    def addTeacher(self, newTeacher: schemas.TeacherCreate):
        tid = secrets.token_hex(8)
        teacherModel = models.Teacher(tid=tid, first=newTeacher.first.upper(), last=newTeacher.last.upper(), school=newTeacher.school)
        self.db.add(teacherModel)
        self.db.commit()
        self.db.refresh(teacherModel)
        return teacherModel

    def addSession(self, newSession: schemas.SessionCreate):
        sid = secrets.token_hex(8)
        sessionModel = models.UserSession(**newSession.dict(), sid=sid, last_accessed=time.time())
        self.db.add(sessionModel)
        self.db.commit()
        self.db.refresh(sessionModel)
        return sessionModel
    
    def removeClass(self, cls: schemas.Class):
        modelClass = models.Class(**cls.dict())
        self.db.delete(modelClass)
        self.db.commit()
        return True

    def removeClassesByUser(self, user: schemas.UserReturn):
        classes = self.getClassesByUser(user)
        for cls in classes:
            self.db.delete(cls)
        self.db.commit()
        return True

    def updateSchedule(self, user: schemas.UserReturn, schedule: schemas.Schedule):
        self.removeClassesByUser(user)
        for cls in schedule:
            for teacher in cls[1]:
                resTeacher = self.getTeacher(schemas.TeacherReturn(tid=None, first=teacher.first, last=teacher.last, school=teacher.school))
                if resTeacher == None:
                    tid = self.addTeacher(schemas.TeacherCreate(first=teacher.first, last=teacher.last, school=user.school)).tid
                else:
                    tid = resTeacher.tid
                self.addClass(schemas.Class(tid=tid, block=ReverseBlockMapper()[cls[0]], uid=user.uid))
        return True
    
    def updateProfile(self, profile: schemas.UserBase, uid: str):
        q = update(models.User).where(models.User.uid == uid).values(**profile.dict()).\
        execution_options(synchronize_session="fetch")
        result = self.db.execute(q)
        self.db.commit()
        return result

crud = CRUD()

# crud.addUser(schemas.StudentBase(first="Roshan", last="Karim", gid=12345, school=SchoolName.NEWTON_NORTH, grade=10))

#t = schemas.TeacherCreate(first="James", last="Black", school=SchoolName.NEWTON_SOUTH)

#crud.addTeacher(t)

# print(crud.getTeacher(t))

#crud.addClass(schemas.Class(tid="261d5388a79592a3", block=SchoolBlock.B, uid="44cadd4a-a51b-43f1-be10-dcb0bb7cc964"))
# #print(getUser(SessionLocal(), "bbd06f42-990d-48de-a7bb-ee98717d4c5d").schedule[0])

