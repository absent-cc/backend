from datetime import datetime, date
from logging import raiseExceptions
import time
import secrets
from typing import List, Optional, Tuple
from xxlimited import new
from loguru import logger
from uuid import uuid4
from sqlalchemy import update

from ..dataTypes import schemas, models, structs
from ..utils.prettifyTeacherName import prettify

def getUser(db, user: schemas.UserReturn) -> models.User:
    if user.uid != None:
        logger.info("User looked up: " + user.uid) # Logs lookup.
        return db.query(models.User).filter(models.User.uid == user.uid).first() # Grabs the first entry of the model User that matches UID.
    if user.gid != None:
        logger.info("User looked up: " + user.gid) # Logs lookup.
        return db.query(models.User).filter(models.User.gid == user.gid).first() # Grabs the first entry of the model User that matches GID.
    return None

def getTeacher(db, teacher: schemas.TeacherReturn) -> models.Teacher:
    if teacher.tid != None:
        return db.query(models.Teacher).filter(models.Teacher.tid == teacher.tid).first() # Looks up teacher by TID if available, grabs the first match.
    if teacher.first != None and teacher.last != None and teacher.school != None: # Does so below by name and school, these entries are treated as a primary key by our DB.
        return db.query(models.Teacher).filter(models.Teacher.first == teacher.first, models.Teacher.last == teacher.last).first()
    return None

def getSession(db, session: schemas.SessionReturn) -> models.UserSession:
    if session.sid != None and session.uid != None: # These two values are used to look up sessions, much exist.
        q = update(models.UserSession).where(models.UserSession.uid == session.uid, models.UserSession.sid == session.sid).values(last_accessed=datetime.now()).\
        execution_options(synchronize_session="fetch") # Updates last accessed time.
        db.execute(q)
        db.commit()
        
        logger.info("Session looked up: " + session.sid + '.' + session.uid) # Logs the lookup. This essentially behaves as an access log as the accounts code calls this to verify sessions.
        return db.query(models.UserSession).filter(models.UserSession.uid == session.uid, models.UserSession.sid == session.sid).first() # Returns session information.
    return None

def getAllUsers(db) -> List[models.User]:
    return db.query(models.User).all()

def getUsersByName(db, first, last) -> List[models.User]:
    return db.query(models.User).filter(models.User.first == first.lower(), models.User.last == last.lower()).all()
    
def getUserCount(db) -> int:
    return db.query(models.User).count()

def getSessionList(db, user: schemas.UserReturn) -> List[models.UserSession]:
    if user.uid != None:
        sessions = db.query(models.UserSession).filter(models.UserSession.uid == user.uid).all()
        return sessions
    return None

def getClassesByTeacher(db, teacher: schemas.TeacherReturn, block: structs.SchoolBlock) -> List[models.Class]:
    if teacher.tid != None:
        return db.query(models.Class).filter(models.Class.tid == teacher.tid, models.Class.block == block).all()
    return None

def getClassesByTeacherForDay(db, teacher: schemas.TeacherReturn, day: int) -> List[models.Class]:
    if teacher.tid != None:
        returnClasses = []
        for block in structs.SchoolBlocksOnDay()[day]:
            classes = getClassesByTeacher(db, teacher, block)
            if classes != None:
                returnClasses.append(classes) 
        return returnClasses
    return None

def getAbsenceList(db, searchDate: date=datetime.today().date(), school: Optional[structs.SchoolName] = None) -> List[models.Absence]:
    if school != None:
        absences = db.query(models.Absence).join(models.Teacher).filter(models.Absence.date == searchDate, models.Teacher.school == school.upper()).all()
        return absences
    absences = db.query(models.Absence).filter(models.Absence.date == searchDate).all()
    return absences

def getAbsenceCount(db) -> int:
    return db.query(models.Absence).count()

def getClassesByUser(db, user: schemas.UserReturn) -> List[models.Class]: 
    if user.uid != None:
        return db.query(models.Class).filter(models.Class.uid == user.uid).all() # Returns all entries in classes table for a given user.
    return None

def getClassesCount(db) -> int:
    return db.query(models.Class).count()

def getUserSettings(db, user: schemas.UserReturn) -> models.UserSettings:
    if user.uid != None:
        return db.query(models.UserSettings).filter(models.UserSettings.uid == user.uid).first()
    return None

def addUser(db, user: schemas.UserCreate) -> models.User:
    if user.gid != None: # Checks for GID as this is the only mandatory field.
        uid = str(uuid4()) # Generates UUID.
        userModel = models.User(uid=uid, **user.dict()) # Creates model from dict of input values.
        db.add(userModel)
        db.commit()
        logger.info("User added: " + uid) # Logs the addition.
        return userModel # Returns user details, import as many details are generated here.
    return None

def addClass(db, newClass: schemas.Class) -> models.Class:
    if newClass.tid != None and newClass.uid != None and newClass.block != None: # Checks for the required fields.
        cid = secrets.token_hex(4)
        classModel = models.Class(**newClass.dict(), cid=cid) # Creates a model.
        db.add(classModel) # Adds it.
        db.commit()
        return classModel # Returns class details.
    return None

def addTeacher(db, newTeacher: schemas.TeacherCreate) -> models.Teacher:
    if newTeacher.first != None and newTeacher.last != None and newTeacher.school != None: # Checks for required fields.
        tid = secrets.token_hex(4) # Generates hexadecimal TID.
        newTeacher = prettify(schemas.TeacherReturn(**newTeacher.dict(), tid=tid))
        teacherModel = models.Teacher(**newTeacher.dict()) # Creates a model.
        db.add(teacherModel) # Adds teacher.
        db.commit()
        logger.info("Teacher added: " + tid) # Logs the action.
        return teacherModel
    return None

# def addAbsence(db, absence: schemas.AbsenceCreate, date: datetime = datetime.today().date()) -> models.Absence:
def addAbsence(db, absence: schemas.AbsenceCreate) -> models.Absence:
    if absence.teacher.first != None and absence.teacher.last != None and absence.teacher.school != None:
        teacher = getTeacher(db, schemas.TeacherReturn(**absence.teacher.dict()))
    if teacher == None:
        teacher = addTeacher(db, absence.teacher)
    absenceModel = models.Absence(date=absence.date, tid=teacher.tid, note=absence.note, length=absence.length)
    db.add(absenceModel)
    db.commit()
    return absenceModel

# Peek the top entry in the absences table by date.
def peekAbsence(db, date: datetime) -> tuple:
    query = db.query(models.Absence).filter(models.Absence.date == datetime.today().date()).first()
    return query

def getAllAbsences(db) -> List[models.Absence]:
    return db.query(models.Absence).all()

def getAbsencesCount(db) -> int:
    return len(getAllAbsences(db))

def addSession(db, newSession: schemas.SessionCreate) -> models.UserSession:
    if newSession.uid != None: # Checks for required fields    
        sessions = getSessionList(db, schemas.UserReturn(uid=newSession.uid))
        if len(sessions) >= 6:
            oldestSession = min(sessions, key = lambda t: t.last_accessed)
            removeSession(db, schemas.SessionReturn.from_orm(oldestSession))
        sid = secrets.token_hex(8) # Generates SID.
        sessionModel = models.UserSession(uid=newSession.uid, sid=sid, last_accessed=datetime.now()) # Creates object including timestamp, makes model.
        db.add(sessionModel) # Adds model.
        db.commit()
        logger.info("Session added: " + sid + '.' + newSession.uid) # Logs actions.
        return sessionModel
    return None

def removeSession(db, session: schemas.SessionReturn) -> bool:
    if session.sid != None and session.uid != None:
        db.query(models.UserSession).filter(models.UserSession.uid == session.uid, models.UserSession.sid == session.sid).delete()
        db.commit()
        return True
    return False

def removeUser(db, user: schemas.UserReturn) -> bool:
    if user.uid != None: # Checks for required fields.
        # self.removeClassesByUser(user) # Removes all of a user's classes.
        db.query(models.User).filter(models.User.uid == user.uid).delete() # Removes the user.
        db.commit()
        logger.info("Student removed: " + user.uid) # Logs the action.
        return True
    return False

def removeClass(db, cls: schemas.Class) -> bool:
    if cls.tid != None and cls.uid != None and cls.block != None: # Checks for required fields.
        modelClass = models.Class(**cls.dict()) # Builds model.
        db.delete(modelClass) # Removes it.
        db.commit()
        return True
    return False

def removeClassesByUser(db, user: schemas.UserReturn) -> bool: # Used for updating schedule and cancellation.
    classes = getClassesByUser(db, user) # Gets a student's classes.
    for cls in classes:
        db.delete(cls) # Deletes them all.
    db.commit()
    return True

def removeAbsencesByDate(db, date: datetime) -> bool:
    print("DELETIG ABSENCES on " + str(date))
    db.query(models.Absence).filter(models.Absence.date == date).delete()
    db.commit()
    return True

def updateSchedule(db, user: schemas.UserReturn, schedule: schemas.Schedule) -> bool:
    if user.school == None:
        user = getUser(db, user)
        if user.school == None:
            return False
    if user.uid != None:
        removeClassesByUser(db, user) # Removes all old classes.
        for cls in schedule:
            if cls[1] != None:
                for teacher in cls[1]: # This loops through all the teachers for a given block.
                    resTeacher = getTeacher(db, schemas.TeacherReturn(first=teacher.first, last=teacher.last, school=user.school))
                    if resTeacher == None:
                        tid = addTeacher(db, schemas.TeacherCreate(first=teacher.first, last=teacher.last, school=user.school)).tid # Adds them to DB if they don't exist.
                    else:
                        tid = resTeacher.tid # Else, just reference them.
                    addClass(db, schemas.Class(tid=tid, block=structs.ReverseBlockMapper()[cls[0]], uid=user.uid)) # Creates class entry.
        return True
    return False

def updateProfile(db, profile: schemas.UserBase, uid: str) -> models.User:
    result = db.execute(update(models.User).where(models.User.uid == uid).values(**profile.dict()).execution_options(synchronize_session="fetch"))
    db.commit()
    return result # Returns new profile.

def updateUserSettings(db, settings: schemas.UserSettings, uid: str) -> models.UserSettings:
    db.query(models.UserSettings).where(models.UserSettings.uid == uid).delete()
    settingsModel = models.UserSettings(**settings.dict())
    settingsModel.uid = uid
    db.add(settingsModel)
    db.commit()
    return True
    
def updateFCMToken(db, token: schemas.Token, uid: str, sid: str) -> models.UserSession:
    result = db.execute(update(models.UserSession).where(models.UserSession.uid == uid, models.UserSession.sid == sid).values(fcm_token = token.token, fcm_timestamp = datetime.now()).execution_options(synchronize_session="fetch"))
    db.commit()
    return result

def reset(db):
    print("INTERNAL FLAG: RESETTING DB!")
    db.query(models.User).delete()
    db.query(models.Teacher).delete()
    db.query(models.Class).delete()
    db.query(models.Absence).delete()
    db.query(models.UserSession).delete()
    db.commit()

# Function to check if a user has been onboarded successfully.
# Defintion of onboarded: A user has onboarded successfully when they exist in the user table, as well as have at least one class in the class table.
# Otherwise, they have not onboarded.
# Returns: Tuple[bool, bool] = (exists in users, exists in classes)
def checkOnboarded(db, gid: str = None, uid: str = None) -> Tuple[bool, bool]:
    if gid != None:
        resUser = getUser(db, schemas.UserReturn(gid=gid))
    elif uid != None:
        resUser = getUser(db, schemas.UserReturn(uid=uid))
    else: 
        raise Exception("No gid or uid provided!")
    
    # If user is not in the table, they could not have possibly been onboarded.
    if resUser == None: return (False, False)
    
    # If user is in the table, check if they have any classes.
    resClasses = getClassesByUser(db, resUser)
    
    if len(resClasses) == 0: # Lack of classes means they have not been onboarded fully
        return (True, False)
    else:
        print(f"User has: {resClasses}")
        return (True, True) # If they have classes, they have been onboarded!
