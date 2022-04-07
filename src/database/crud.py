import secrets
from datetime import datetime, date
from typing import List, Optional, Tuple
from uuid import uuid4

from loguru import logger
from sqlalchemy import update

from ..dataTypes import schemas, models, structs
from ..dataTypes.models import Class
from ..utils.prettifyTeacherName import prettify

logger.add(
    "logs/{time:YYYY-MM-DD}/crud.log",
    format="{time} {level} {message}",
    filter="xxlimited",
    level="INFO",
)


def getUser(db, user: schemas.UserReturn) -> models.User:
    if user.uid is not None:
        logger.info("GET User looked up by UID: " + user.uid)  # Logs lookup.
        return (
            db.query(models.User).filter(models.User.uid == user.uid).first()
        )  # Grabs the first entry of the model User that matches UID.
    if user.gid is not None:
        logger.info("GET User looked up by GID: " + user.gid)  # Logs lookup.
        return (
            db.query(models.User).filter(models.User.gid == user.gid).first()
        )  # Grabs the first entry of the model User that matches GID.
    logger.info("GET User FAILED: " + user.uid + " " + user.gid)
    return None


def getTeacher(db, teacher: schemas.TeacherReturn) -> models.Teacher:
    if teacher.tid is not None:
        logger.info("GET Teacher looked up by TID: " + teacher.tid)  # Logs lookup.
        return (
            db.query(models.Teacher).filter(models.Teacher.tid == teacher.tid).first()
        )  # Looks up teacher by TID if available, grabs the first match.
    if (
        teacher.first is not None
        and teacher.last is not None
        and teacher.school is not None
    ):  # Does so below by name and school, these entries are treated as a primary key by our DB.
        logger.info(
            "GET Teacher looked up by Name: "
            + teacher.first
            + " "
            + teacher.last
            + " "
            + teacher.school
        )  # Logs lookup.
        return (
            db.query(models.Teacher)
            .filter(
                models.Teacher.first == teacher.first,
                models.Teacher.last == teacher.last,
            )
            .first()
        )
    logger.info(
        "GET Teacher FAILED: "
        + teacher.tid
        + " "
        + teacher.first
        + " "
        + teacher.last
        + " "
        + teacher.school
    )
    return None


def getAllTeachersBySchool(db, school: structs.SchoolName) -> List[models.Teacher]:
    if school is not None:
        logger.info("GET teachers by school requested: " + school)
        return db.query(models.Teacher).filter(models.Teacher.school == school).all()
    return []


def getSession(db, session: schemas.SessionReturn) -> models.UserSession:
    if (
        session.sid is not None and session.uid is not None
    ):  # These two values are used to look up sessions, much exist.
        q = (
            update(models.UserSession)
            .where(
                models.UserSession.uid == session.uid,
                models.UserSession.sid == session.sid,
            )
            .values(last_accessed=datetime.now())
            .execution_options(synchronize_session="fetch")
        )  # Updates last accessed time.
        db.execute(q)
        db.commit()

        logger.info(
            "GET Session looked up: " + session.sid + "." + session.uid
        )  # Logs the lookup. This essentially behaves as an access log as the accounts code calls this to verify sessions.
        return (
            db.query(models.UserSession)
            .filter(
                models.UserSession.uid == session.uid,
                models.UserSession.sid == session.sid,
            )
            .first()
        )  # Returns session information.
    logger.info("GET Session FAILED: " + session.sid + "." + session.uid)
    return None


def getAllUsers(db) -> List[models.User]:
    logger.info("GET all users requested")
    return db.query(models.User).all()


def getUsersBySchool(db, school: structs.SchoolName):
    logger.info("GET users by school requested: " + school)
    return db.query(models.User).filter(models.User.school == school).all()


def getUsersByName(db, first, last) -> List[models.User]:
    logger.info("GET users by name requested: " + first + " " + last)
    return (
        db.query(models.User)
        .filter(models.User.first == first.lower(), models.User.last == last.lower())
        .all()
    )


def getUserCount(db) -> int:
    logger.info("GET user count requested")
    return db.query(models.User).count()


def getSessionList(db, user: schemas.UserReturn) -> List[models.UserSession]:
    if user.uid is not None:
        sessions = (
            db.query(models.UserSession)
            .filter(models.UserSession.uid == user.uid)
            .all()
        )
        logger.info("GET session list requested for user: " + user.uid)
        return sessions
    logger.info("GET session list FAILED for user: " + user.uid)
    return None


def getClassesByTeacher(
    db, teacher: schemas.TeacherReturn, block: structs.SchoolBlock
) -> List[models.Class]:
    if teacher.tid is not None:
        logger.info("GET classes by teacher requested: " + teacher.tid + " " + block)
        return (
            db.query(models.Class)
            .filter(models.Class.tid == teacher.tid, models.Class.block == block)
            .all()
        )
    logger.info("GET classes by teacher FAILED: " + teacher.tid + " " + block)
    return None


def getClassesByTeacherForDay(
    db, teacher: schemas.TeacherReturn, day: int
) -> list[list[Class]]:
    if teacher.tid is not None:
        returnClasses = []
        # for block in structs.SchoolBlocksOnDay()[day]:
        for block in structs.SchoolBlocksOnDayWithTimes()[day].blocks():
            classes = getClassesByTeacher(db, teacher, block)
            if classes is not None:
                returnClasses.append(classes)
        logger.info("GET classes by teacher requested: " + teacher.tid + " " + str(day))
        return returnClasses
    logger.info("GET classes by teacher FAILED: " + teacher.tid + " " + str(day))
    return None


def getClassesByTeacherForDate(
    db, teacher: schemas.TeacherReturn, date: date
) -> list[list[Class]]:
    if teacher.tid is not None:
        returnClasses = []
        blocks: structs.ScheduleWithTimes = getSchoolDaySchedule(db, date)
        for block in blocks.blocks():
            classes = getClassesByTeacher(db, teacher, block)
            if classes is not None:
                returnClasses.append(classes)
        logger.info(
            "GET classes by teacher requested: " + teacher.tid + " " + str(date)
        )
        return returnClasses
    logger.info("GET classes by teacher FAILED: " + teacher.tid + " " + str(date))
    return None


def getAbsenceList(
    db,
    searchDate: date = datetime.today().date(),
    school: Optional[structs.SchoolName] = None,
) -> List[models.Absence]:
    if school is not None:
        absences = (
            db.query(models.Absence)
            .join(models.Teacher)
            .filter(models.Absence.date == searchDate, models.Teacher.school == school)
            .all()
        )
        logger.info(
            "GET absence list requested by school: " + school + " " + str(searchDate)
        )
        return absences
    absences = db.query(models.Absence).filter(models.Absence.date == searchDate).all()
    logger.info("GET absence list requested in general: " + str(searchDate))
    return absences


def getAbsenceCount(db) -> int:
    logger.info("GET absence count requested")
    return db.query(models.Absence).count()


def getClassesByUser(db, user: schemas.UserReturn) -> List[models.Class]:
    if user.uid is not None:
        logger.info("GET classes by user requested: " + user.uid)
        return (
            db.query(models.Class).filter(models.Class.uid == user.uid).all()
        )  # Returns all entries in classes table for a given user.
    logger.info("GET classes by user FAILED: " + user.uid)
    return None


def getClassesCount(db) -> int:
    logger.info("GET classes count requested")
    return db.query(models.Class).count()


def getUserSettings(db, user: schemas.UserReturn) -> models.UserSettings:
    if user.uid is not None:
        logger.info("GET user settings requested: " + user.uid)
        return (
            db.query(models.UserSettings)
            .filter(models.UserSettings.uid == user.uid)
            .first()
        )
    logger.info("GET user settings FAILED: " + user.uid)
    return None


def getAlwaysNotify(db, school: structs.SchoolName) -> models.User:
    logger.info("GET always notify people")
    return (
        db.query(models.UserSettings)
        .join(models.User)
        .filter(
            models.UserSettings.notifyWhenNone == True, models.User.school == school
        )
        .all()
    )


# Peek the top entry in the absences table by date.
def peekAbsence(db, date: datetime) -> tuple:
    query = (
        db.query(models.Absence)
        .filter(models.Absence.date == datetime.today().date())
        .first()
    )
    logger.info(f"PEEK Absence requested: {query.date}")
    return query


def getAllAbsences(db) -> List[models.Absence]:
    logger.info("GET all absences requested")
    return db.query(models.Absence).all()


def getAbsencesCount(db) -> int:
    logger.info("GET absences count requested")
    return len(getAllAbsences(db))


def getSpecialDay(db, date: date) -> models.SpecialDays:
    logger.info(f"GET special day requested: {date}")
    return db.query(models.SpecialDays).filter(models.SpecialDays.date == date).first()


def getSchoolDaySchedule(db, date: date) -> structs.ScheduleWithTimes:
    logger.info("GET school day schedule requested: " + str(date))
    specialDayCheck: models.SpecialDays = getSpecialDay(db, date)
    if specialDayCheck is not None:
        return specialDayCheck.schedule
    return structs.SchoolBlocksOnDayWithTimes()[date.weekday()]


def addSpecialDay(db, specialDay: schemas.SpecialDay) -> bool:
    logger.info(f"ADD special day requested: {specialDay.date}")
    try:
        db.add(
            models.SpecialDays(
                date=specialDay.date,
                name=specialDay.name,
                schedule=specialDay.schedule,
                note=specialDay.note,
            )
        )
    except Exception as e:
        logger.error(f"ADD special day failed: {e}")
        return False
    db.commit()
    return True


def addUser(db, user: schemas.UserCreate) -> models.User:
    if user.gid is not None:  # Checks for GID as this is the only mandatory field.
        uid = str(uuid4())  # Generates UUID.
        userModel = models.User(
            uid=uid, **user.dict()
        )  # Creates model from dict of input values.
        db.add(userModel)
        db.commit()
        logger.info(
            "ADD User added by GID: " + user.gid + "Created UID:" + uid
        )  # Logs the addition.
        return userModel  # Returns user details, import as many details are generated here.
    logger.info("ADD User add FAILED: " + user.gid)
    return None


def addClass(db, newClass: schemas.Class) -> models.Class:
    if (
        newClass.tid is not None
        and newClass.uid is not None
        and newClass.block is not None
    ):  # Checks for the required fields.
        cid = secrets.token_hex(4)
        classModel = models.Class(**newClass.dict(), cid=cid)  # Creates a model.
        db.add(classModel)  # Adds it.
        db.commit()
        logger.info(
            f"ADD Class: {cid} | TID: {newClass.tid} UID: {newClass.uid} block: {newClass.block}"
        )  # Logs the addition.
        return classModel  # Returns class details.
    logger.info(
        f"ADD Class FAILED | TID: {newClass.tid} UID: {newClass.uid} block: {newClass.block}"
    )
    return None


def addTeacher(db, newTeacher: schemas.TeacherCreate) -> models.Teacher:
    if (
        newTeacher.first is not None
        and newTeacher.last is not None
        and newTeacher.school is not None
    ):  # Checks for required fields.
        tid = secrets.token_hex(4)  # Generates hexadecimal TID.
        newTeacher = prettify(schemas.TeacherReturn(**newTeacher.dict(), tid=tid))
        teacherModel = models.Teacher(**newTeacher.dict())  # Creates a model.
        db.add(teacherModel)  # Adds teacher.
        db.commit()
        logger.info(
            f"ADD Teacher: {tid} | First: {newTeacher.first} Last: {newTeacher.last} School: {newTeacher.school}"
        )  # Logs the addition.
        return teacherModel
    logger.info(
        f"ADD Teacher FAILED | First: {newTeacher.first} Last: {newTeacher.last} School: {newTeacher.school}"
    )
    return None


# def addAbsence(db, absence: schemas.AbsenceCreate, date: datetime = datetime.today().date()) -> models.Absence:
def addAbsence(db, absence: schemas.AbsenceCreate) -> models.Absence:
    if (
        absence.teacher.first is not None
        and absence.teacher.last is not None
        and absence.teacher.school is not None
    ):
        teacher = getTeacher(db, schemas.TeacherReturn(**absence.teacher.dict()))
    if teacher is None:
        teacher = addTeacher(db, absence.teacher)
    absenceModel = models.Absence(
        date=absence.date, tid=teacher.tid, note=absence.note, length=absence.length
    )
    db.add(absenceModel)
    db.commit()
    logger.info(f"ADD Absence: {absence.date} | TID: {teacher.tid}")
    return absenceModel


def addSession(db, newSession: schemas.SessionCreate) -> models.UserSession:
    if newSession.uid is not None:  # Checks for required fields
        sessions = getSessionList(db, schemas.UserReturn(uid=newSession.uid))
        if len(sessions) >= 6:
            oldestSession = min(sessions, key=lambda t: t.last_accessed)
            removeSession(db, schemas.SessionReturn.from_orm(oldestSession))
        sid = secrets.token_hex(8)  # Generates SID.
        sessionModel = models.UserSession(
            uid=newSession.uid, sid=sid, last_accessed=datetime.now()
        )  # Creates object including timestamp, makes model.
        db.add(sessionModel)  # Adds model.
        db.commit()
        logger.info("ADD Session: " + sid + "." + newSession.uid)  # Logs actions.
        return sessionModel
    logger.info("ADD Session FAILED: " + newSession.uid)
    return None


def removeSession(db, session: schemas.SessionReturn) -> bool:
    if session.sid is not None and session.uid is not None:
        db.query(models.UserSession).filter(
            models.UserSession.uid == session.uid, models.UserSession.sid == session.sid
        ).delete()
        db.commit()
        logger.info("REMOVE Session: " + session.sid + "." + session.uid)
        return True
    logger.info("REMOVE Session FAILED: " + session.sid)
    return False


def removeUser(db, user: schemas.UserReturn) -> bool:
    if user.uid is not None:  # Checks for required fields.
        # self.removeClassesByUser(user) # Removes all of a user's classes.
        db.query(models.User).filter(
            models.User.uid == user.uid
        ).delete()  # Removes the user.
        db.commit()
        logger.info("REMOVE Student: " + user.uid)  # Logs the action.
        return True
    logger.info("REMOVE Student: " + user.uid)
    return False


def removeClass(db, cls: schemas.Class) -> bool:
    if (
        cls.tid is not None and cls.uid is not None and cls.block is not None
    ):  # Checks for required fields.
        modelClass = models.Class(**cls.dict())  # Builds model.
        db.delete(modelClass)  # Removes it.
        db.commit()
        logger.info(
            "REMOVE Class: "
            + "TID:"
            + cls.tid
            + " UID:"
            + cls.uid
            + " block:"
            + cls.block
        )  # Logs the action.
        return True
    logger.info(
        "REMOVE Class FAILED: "
        + "TID:"
        + cls.tid
        + " UID:"
        + cls.uid
        + " block:"
        + cls.block
    )
    return False


def removeSpecialDay(db, date: date) -> bool:
    logger.info(f"REMOVE special day requested: {date}")
    try:
        db.query(models.SpecialDays).filter(models.SpecialDays.date == date).delete()
    except Exception as e:
        logger.error(f"REMOVE special day failed: {e}")
        return False
    return True


def removeClassesByUser(
    db, user: schemas.UserReturn
) -> bool:  # Used for updating schedule and cancellation.
    classes: List[models.Class] = getClassesByUser(
        db, user
    )  # Gets a student's classes.
    for cls in classes:
        db.delete(cls)  # Deletes them all.
        logger.info(
            "REMOVING Class: "
            + "TID:"
            + cls.tid
            + " UID:"
            + cls.uid
            + " block:"
            + cls.block
        )
    db.commit()
    logger.info(
        "REMOVE End of removing all classes for UID:" + user.uid
    )  # Logs the action.
    return True


def removeAbsencesByDate(db, date: datetime) -> bool:
    db.query(models.Absence).filter(models.Absence.date == date).delete()
    db.commit()
    logger.info("REMOVE Absences for date: " + str(date))
    return True


def updateSchedule(db, user: schemas.UserReturn, schedule: schemas.Schedule) -> bool:
    if user.school is None:
        user = getUser(db, user)
        if user.school is None:
            logger.info("UPDATE Schedule FAILED: " + user.uid + " has no school.")
            return False

    if user.uid is not None:
        removeClassesByUser(db, user)  # Removes all old classes.
        logger.info(
            "REMOVED all classes for UID: "
            + user.uid
            + " | Operation for updateSchedule."
        )
        for cls in schedule:
            if cls[1] is not None:
                for teacher in cls[
                    1
                ]:  # This loops through all the teachers for a given block.
                    resTeacher = getTeacher(
                        db,
                        schemas.TeacherReturn(
                            first=teacher.first, last=teacher.last, school=user.school
                        ),
                    )
                    if resTeacher is None:
                        tid = addTeacher(
                            db,
                            schemas.TeacherCreate(
                                first=teacher.first,
                                last=teacher.last,
                                school=user.school,
                            ),
                        ).tid  # Adds them to DB if they don't exist.
                    else:
                        tid = resTeacher.tid  # Else, just reference them.
                    addClass(
                        db,
                        schemas.Class(
                            tid=tid,
                            block=structs.ReverseBlockMapper()[cls[0]],
                            uid=user.uid,
                        ),
                    )  # Creates class entry.
        logger.info("UPDATE Schedule succesful for UID: " + user.uid)
        return True
    logger.info("UPDATE Schedule returned FALSE. No UID provided.")
    return False


def updateProfile(db, profile: schemas.UserBase, uid: str) -> models.User:
    result = db.execute(
        update(models.User)
        .where(models.User.uid == uid)
        .values(**profile.dict())
        .execution_options(synchronize_session="fetch")
    )
    db.commit()
    logger.info("UPDATE Profile: " + uid)
    return result  # Returns new profile.


def updateUserSettings(db, settings: schemas.UserSettings, uid: str) -> bool:
    db.query(models.UserSettings).where(models.UserSettings.uid == uid).delete()
    settingsModel = models.UserSettings(**settings.dict())
    settingsModel.uid = uid
    db.add(settingsModel)
    db.commit()
    logger.info("UPDATE UserSettings: " + uid)
    return True


def updateFCMToken(db, token: schemas.Token, uid: str, sid: str) -> models.UserSession:
    result = db.execute(
        update(models.UserSession)
        .where(models.UserSession.uid == uid, models.UserSession.sid == sid)
        .values(fcm_token=token.token, fcm_timestamp=datetime.now())
        .execution_options(synchronize_session="fetch")
    )
    db.commit()
    logger.info("UPDATE FCM Token: " + uid + "." + sid)
    return result


def reset(db):
    print("INTERNAL FLAG: RESETTING DB!")
    db.query(models.User).delete()
    db.query(models.Teacher).delete()
    db.query(models.Class).delete()
    db.query(models.Absence).delete()
    db.query(models.UserSession).delete()
    db.query(models.SpecialDays).delete()
    db.commit()
    logger.info("RESET DB!!!!!")


# Function to check if a user has been onboarded successfully.
# Defintion of onboarded: A user has onboarded successfully when they exist in the user table, as well as have at least one class in the class table.
# Otherwise, they have not onboarded.
# Returns: Tuple[bool, bool] = (exists in users, exists in classes)
def checkOnboarded(db, gid: str = None, uid: str = None) -> Tuple[bool, bool]:
    if gid is not None:
        resUser = getUser(db, schemas.UserReturn(gid=gid))
    elif uid is not None:
        resUser = getUser(db, schemas.UserReturn(uid=uid))
    else:
        raise Exception("No gid or uid provided!")

    # If user is not in the table, they could not have possibly been onboarded.
    if resUser is None:
        logger.info("CHECK User not onboarded: User does not exist in users table.")
        return False, False

    # If user is in the table, check if they have any classes.
    resClasses = getClassesByUser(db, resUser)

    if len(resClasses) == 0:  # Lack of classes means they have not been onboarded fully
        logger.info("CHECK User " + resUser.uid + " has not been onboarded.")
        return True, False
    else:
        logger.info("CHECK User " + resUser.uid + " has been onboarded.")
        return True, True  # If they have classes, they have been onboarded!
