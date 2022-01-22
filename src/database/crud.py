from datetime import datetime
import time
import secrets
from typing import List
from loguru import logger
from uuid import uuid4
from sqlalchemy import update

from dataTypes import schemas, models, structs
from database.database import SessionLocal

class CRUD:
    def __init__(self):
        self.db = SessionLocal()

    def terminate(self) -> bool:
        self.db.close()
        return True

    def getUser(self, user: schemas.UserReturn) -> models.User:
        if user.uid != None:
            logger.info("User looked up: " + user.uid) # Logs lookup.
            return self.db.query(models.User).filter(models.User.uid == user.uid).first() # Grabs the first entry of the model User that matches UID.
        if user.gid != None:
            logger.info("User looked up: " + user.gid) # Logs lookup.
            return self.db.query(models.User).filter(models.User.gid == user.gid).first() # Grabs the first entry of the model User that matches GID.
        return None

    def getTeacher(self, teacher: schemas.TeacherReturn) -> models.Teacher:
        if teacher.tid != None:
            return self.db.query(models.Teacher).filter(models.Teacher.tid == teacher.tid).first() # Looks up teacher by TID if available, grabs the first match.
        if teacher.first != None and teacher.last != None and teacher.school != None: # Does so below by name and school, these entries are treated as a primary key by our DB.
            return self.db.query(models.Teacher).filter(models.Teacher.first == teacher.first.upper(), models.Teacher.last == teacher.last.upper()).first()
        return None

    def getSession(self, session: schemas.SessionReturn) -> models.UserSession:
        if session.sid != None and session.uid != None: # These two values are used to look up sessions, much exist.
            q = update(models.UserSession).where(models.UserSession.uid == session.uid, models.UserSession.sid == session.sid).values(last_accessed=datetime.now()).\
            execution_options(synchronize_session="fetch") # Updates last accessed time.
            self.db.execute(q)
            self.db.commit()
            
            logger.info("Session looked up: " + session.sid + '.' + session.uid) # Logs the lookup. This essentially behaves as an access log as the accounts code calls this to verify sessions.
            return self.db.query(models.UserSession).filter(models.UserSession.uid == session.uid, models.UserSession.sid == session.sid).first() # Returns session information.
        return None

    def getAbsenceList(self) -> tuple:
        absences = self.db.query(models.Absence).filter(models.Absence.date == datetime.today()).all()
        return absences

    # def getClass(self, cls: schemas.Class): # Completely useless function. DEP.
    #     if cls.tid != None and cls.uid != None and cls.block != None: 
    #         return self.db.query(models.Class).filter(models.Class.tid == cls.tid, models.Class.uid == cls.uid, models.Class.block == cls.block).first()
    #     return None

    def getClassesByUser(self, user: schemas.UserReturn) -> List[models.Class]: 
        if user.uid != None:
            return self.db.query(models.Class).filter(models.Class.uid == user.uid).all() # Returns all entries in classes table for a given user.
        return None

    def addUser(self, user: schemas.UserCreate) -> models.User:
        if user.gid != None: # Checks for GID as this is the only mandatory field.
            uid = str(uuid4()) # Generates UUID.
            userModel = models.User(uid=uid, **user.dict()) # Creates model from dict of input values.
            self.db.add(userModel)
            self.db.commit()
            logger.info("User added: " + uid) # Logs the addition.
            return userModel # Returns user details, import as many details are generated here.
        return None

    def addClass(self, newClass: schemas.Class) -> models.Class:
        if newClass.tid != None and newClass.uid != None and newClass.block != None: # Checks for the required fields.
            classModel = models.Class(**newClass.dict()) # Creates a model.
            self.db.add(classModel) # Adds it.
            self.db.commit()
            return classModel # Returns class details.
        return None

    def addTeacher(self, newTeacher: schemas.TeacherCreate) -> models.Teacher:
        if newTeacher.first != None and newTeacher.last != None and newTeacher.school != None: # Checks for required fields.
            tid = secrets.token_hex(4) # Generates hexadecimal TID.
            teacherModel = models.Teacher(tid=tid, first=newTeacher.first.upper(), last=newTeacher.last.upper(), school=newTeacher.school) # Creates a model.
            self.db.add(teacherModel) # Adds teacher.
            self.db.commit()
            logger.info("Teacher added: " + tid) # Logs the action.
            return teacherModel
        return None

    def addAbsence(self, absence: schemas.AbsenceCreate) -> models.Absence:
        if absence.teacher.tid != None:
            tid = absence.teacher.tid
        elif absence.teacher.first != None and absence.teacher.last != None and absence.teacher.school != None:
            tid = self.getTeacher(absence.teacher)
        if tid != None:
            absenceModel = models.Absence(date=datetime.today(), tid=tid, note=absence.note)
            self.db.add(absenceModel)
            self.db.commit()
            return absenceModel
        return None

    def addSession(self, newSession: schemas.SessionCreate) -> models.UserSession:
        if newSession.uid != None: # Checks for required fields.
            
            sessions = self.db.query(models.UserSession).filter(models.UserSession.uid == newSession.uid).all()
            if len(sessions) >= 6:
                oldestSession = min(sessions, key = lambda t: t.last_accessed)
                self.removeSession(schemas.SessionReturn.from_orm(oldestSession))

            sid = secrets.token_hex(8) # Generates SID.
            sessionModel = models.UserSession(uid=newSession.uid, sid=sid, last_accessed=datetime.now()) # Creates object including timestamp, makes model.
            self.db.add(sessionModel) # Adds model.
            self.db.commit()
            logger.info("Session added: " + sid + '.' + newSession.uid) # Logs actions.
            return sessionModel
        return None

    def removeSession(self, session: schemas.SessionReturn) -> bool:
        if session.sid != None and session.uid != None:
            self.db.query(models.UserSession).filter(models.UserSession.uid == session.uid, models.UserSession.sid == session.sid).delete()
            self.db.commit()
            return True
        return False

    def removeUser(self, user: schemas.UserReturn) -> bool:
        if user.uid != None: # Checks for required fields.
            # self.removeClassesByUser(user) # Removes all of a user's classes.
            self.db.query(models.User).filter(models.User.uid == user.uid).delete() # Removes the user.
            self.db.commit()
            logger.info("Student removed: " + user.uid) # Logs the action.
            return True
        return False

    def removeClass(self, cls: schemas.Class) -> bool:
        if cls.tid != None and cls.uid != None and cls.block != None: # Checks for required fields.
            modelClass = models.Class(**cls.dict()) # Builds model.
            self.db.delete(modelClass) # Removes it.
            self.db.commit()
            return True
        return False

    def removeClassesByUser(self, user: schemas.UserReturn) -> bool: # Used for updating schedule and cancellation.
        classes = self.getClassesByUser(user) # Gets a student's classes.
        for cls in classes:
            self.db.delete(cls) # Deletes them all.
        self.db.commit()
        return True

    def updateSchedule(self, user: schemas.UserReturn, schedule: schemas.Schedule) -> bool:
        if user.school == None:
            user = self.getUser(user)
            if user.school == None:
                return False
        if user.uid != None:
            self.removeClassesByUser(user) # Removes all old classes.
            for cls in schedule:
                if cls[1] != None:
                    for teacher in cls[1]: # This loops through all the teachers for a given block.
                        resTeacher = self.getTeacher(schemas.TeacherReturn(first=teacher.first, last=teacher.last, school=teacher.school))
                        if resTeacher == None:
                            tid = self.addTeacher(schemas.TeacherCreate(first=teacher.first, last=teacher.last, school=user.school)).tid # Adds them to DB if they don't exist.
                        else:
                            tid = resTeacher.tid # Else, just reference them.
                        self.addClass(schemas.Class(tid=tid, block=structs.ReverseBlockMapper()[cls[0]], uid=user.uid)) # Creates class entry.
            return True
        return False
    
    def updateProfile(self, profile: schemas.UserBase, uid: str) -> models.User:
        q = update(models.User).where(models.User.uid == uid).values(**profile.dict()).\
            execution_options(synchronize_session="fetch") # This is the update query, just sets the values to those of the profile dict.
        result = self.db.execute(q)
        self.db.commit()
        return result # Returns new profile.

    def updateFCMToken(self, token: schemas.Token, uid: str, sid: str) -> models.UserSession:
        q = update(models.UserSession).where(models.UserSession.uid == uid, models.UserSession.sid == sid).values(fcm_token = token.token, fcm_timestamp = datetime.now()).\
            execution_options(synchronize_session="fetch")
        result = self.db.execute(q)
        self.db.commit()
        return result