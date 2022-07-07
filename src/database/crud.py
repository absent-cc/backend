from inspect import getfile
import secrets
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional, Tuple
from uuid import uuid4

from loguru import logger
from sqlalchemy import update

from ..dataTypes import schemas, models, structs
from ..utils.prettifyTeacherName import prettifyName, prettifyTeacher


def getUser(db: Session, user: schemas.UserReturn) -> Optional[models.User]:
    if user.uid is not None:
        logger.info(f"GET: User looked up by UID: {user.uid}")  # Logs lookup.
        return (
            db.query(models.User).filter(models.User.uid == user.uid).first()
        )  # Grabs the first entry of the model User that matches UID.
    if user.gid is not None:
        logger.info(f"GET: User looked up by GID: {user.gid}")  # Logs lookup.
        return (
            db.query(models.User).filter(models.User.gid == user.gid).first()
        )  # Grabs the first entry of the model User that matches GID.
    logger.error(f"GET: User lookup failed: {user.uid} {user.gid}")
    return None


def getTeacher(db: Session, teacher: schemas.TeacherReturn) -> Optional[models.Teacher]:
    if teacher.tid is not None:
        logger.info(f"GET: Teacher looked up by TID: {teacher.tid}")  # Logs lookup.
        return (
            db.query(models.Teacher).filter(models.Teacher.tid == teacher.tid).first()
        )  # Looks up teacher by TID if available, grabs the first match.
    if (
        teacher.first is not None
        and teacher.last is not None
        and teacher.school is not None
    ):  # Does so below by name and school, these entries are treated as a primary key by our DB.
        logger.info(
            f"GET: Teacher looked up by name: {teacher.first} {teacher.last} {teacher.school}"
        )  # Logs lookup.
        return (
            db.query(models.Teacher)
            .filter(
                models.Teacher.first == teacher.first,
                models.Teacher.last == teacher.last,
            )
            .first()
        )
    logger.error(
        f"GET: Teacher lookup failed: {teacher.first} {teacher.last} {teacher.school}"
    )
    return None


def getSession(db: Session, session: schemas.SessionReturn) -> Optional[models.UserSessions]:
    if (
        session.sid is not None and session.uid is not None
    ):  # These two values are used to look up sessions, much exist.
        q = (
            update(models.UserSessions)
            .where(
                models.UserSessions.uid == session.uid,
                models.UserSessions.sid == session.sid,
            )
            .values(last_accessed=datetime.now())
            .execution_options(synchronize_session="fetch")
        )  # Updates last accessed time.
        db.execute(q)
        db.commit()

        logger.info(
            f"GET: Session looked up: {session.sid}.{session.uid}"
        )  # Logs the lookup. This essentially behaves as an access log as the accounts code calls this to verify sessions.
        return (
            db.query(models.UserSessions)
            .filter(
                models.UserSessions.uid == session.uid,
                models.UserSessions.sid == session.sid,
            )
            .first()
        )  # Returns session information.
    logger.error(f"GET: Session lookup failed: + {session.sid}.{session.uid}")
    return None


def getAllUsers(db: Session) -> List[models.User]:
    logger.info("GET: Looked up all users")
    return db.query(models.User).all()


def getUsersByName(db: Session, first: str, last: str) -> List[models.User]:
    logger.info(f"GET: Looked up user by name: {first} {last}")
    return (
        db.query(models.User)
        .filter(models.User.first== first, models.User.last == last)
        .all()
    )


def getUserCount(db: Session) -> int:
    logger.info(f"GET: Looked up user count")
    return db.query(models.User).count()


def getSessionList(db: Session, user: schemas.UserReturn) -> Optional[List[models.UserSessions]]:
    if user.uid is not None:
        sessions = (
            db.query(models.UserSessions)
            .filter(models.UserSessions.uid == user.uid)
            .all()
        )
        logger.info(f"GET: Session list requested for user: {user.uid}")
        return sessions
    logger.error(f"GET: Session list lookup failed for user: {user.uid}")
    return None


def getAbsenceList(
    db: Session,
    searchDate: date = datetime.today().date(),
    school: Optional[structs.SchoolName] = None,
) -> List[models.Absences]:
    if school is not None:
        absences = (
            db.query(models.Absences)
            .join(models.Teacher)
            .filter(models.Absences.date == searchDate, models.Teacher.school == school)
            .all()
        )
        logger.info(
            f"GET: Absence list requested for school: {school} on: {str(searchDate)}"
        )
        return absences
    absences = db.query(models.Absences).filter(models.Absences.date == searchDate).all()
    logger.info(f"GET: Absence list requested for + {str(searchDate)}")
    return absences


def getAbsenceCount(db: Session) -> int:
    logger.info("GET: Absence count requested")
    return db.query(models.Absences).count()


def getClassesByUser(db: Session, user: schemas.UserReturn) -> Optional[List[models.Classes]]:
    if user.uid is not None:
        logger.info(f"GET: User class list requested: {user.uid}")
        return (
            db.query(models.Classes).filter(models.Classes.uid == user.uid).all()
        )  # Returns all entries in classes table for a given user.
    logger.error(f"GET: User class list lookup failed: {user.uid}")
    return None

def getClass(db: Session, cls: schemas.Class) -> Optional[models.Classes]:
    if cls.uid and cls.tid and cls.block:
        logger.info(f"GET: Class lookup requested: {cls.uid} {cls.tid} {cls.block}")
        return (
            db.query(models.Classes)
            .filter(models.Classes.uid == cls.uid, models.Classes.tid == cls.tid, models.Classes.block == cls.block)
            .first()
        )
    logger.error(f"GET: Class lookup failed: {cls.uid} {cls.tid} {cls.block}")
    return None

def getCanceled(db: Session, canceled: schemas.Canceled) -> Optional[models.Canceled]:
    cls = getClass(db, canceled.cls)

    if cls is None:
        logger.error(f"GET: Canceled lookup failed: {canceled.cls.uid} {canceled.cls.tid} {canceled.cls.block}")
        return None
    if canceled.date is None:
        logger.error(f"GET: Canceled lookup failed. Needs a date.")
        return None
    
    logger.info(f"GET: Canceled lookup requested: {canceled.date} {canceled.cls.tid} {canceled.cls.uid} {canceled.cls.block}")
    return (
        db.query(models.Canceled)
        .filter(
            models.Canceled.date == canceled.date,
            models.Canceled.cid == cls.cid,
        )
        .first()
    )


def getClassesCount(db: Session) -> int:
    logger.info("GET: Class count requested.")
    return db.query(models.Classes).distinct(models.Classes.block, models.Classes.tid).count()


def getUserSettings(db: Session, user: schemas.UserReturn) -> Optional[models.UserSettings]:
    if user.uid is not None:
        logger.info(f"GET: User settings requested: {user.uid}")
        return (
            db.query(models.UserSettings)
            .filter(models.UserSettings.uid == user.uid)
            .first()
        )
    logger.error(f"GET: User settings lookup failed: {user.uid}")
    return None


def getAlwaysNotify(db: Session, school: structs.SchoolName) -> models.User:
    logger.info("GET: Looked up users to always notify")
    return (
        db.query(models.UserSettings)
        .join(models.User)
        .filter(
            models.UserSettings.notifyWhenNone == True, models.User.school == school
        )
        .all()
    )

def getTeacherAliasByTID(db: Session, teacher: schemas.TeacherReturn) -> Optional[models.Aliases]:
    if teacher.tid is not None:
        logger.info(f"GET: Teacher alias requested: {teacher.tid}")
        return (
            db.query(models.Aliases)
            .filter(models.Aliases.tid == teacher.tid)
            .first()
        )
    logger.error(f"GET: Teacher alias lookup failed: {teacher.tid}")
    return None

def getTeacherAlias(db: Session, teacher: schemas.TeacherAliasBase) -> models.Aliases:
    if teacher.first is not None and teacher.last is not None:
        logger.info(f"GET: Teacher alias requested: {teacher.first} {teacher.last}")
        return (
            db.query(models.Aliases)
            .filter(
                models.Aliases.first == teacher.first,
                models.Aliases.last == teacher.last,
            )
            .first()
        )
    logger.error(f"GET: Teacher alias lookup failed: {teacher.first} {teacher.last}")
    return None

# Peek the top entry in the absences table by date.
def peekAbsence(db: Session, date: date = datetime.today().date()) -> tuple:
    query = (
        db.query(models.Absences)
        .filter(models.Absences.date == date)
        .first()
    )
    logger.info(f"PEEK: First absence requested: {query.date}")
    return query


def getAbsencesCount(db: Session) -> int:
    logger.info("GET: Absence count requested")
    return db.query(models.Absences).count()


def getSpecialDay(db: Session, date: date) -> models.SpecialDays:
    logger.info(f"GET: Special day lookup requested: {date}")
    return db.query(models.SpecialDays).filter(models.SpecialDays.date == date).first()


def getSchoolDaySchedule(db: Session, date: date) -> structs.ScheduleWithTimes:
    logger.info(f"GET: School day schedule requested: {str(date)}")
    specialDayCheck: models.SpecialDays = getSpecialDay(db, date)
    if specialDayCheck is not None:
        return specialDayCheck.schedule
    return structs.SchoolBlocksOnDayWithTimes()[date.weekday()]

def getAnnouncementByID(db: Session, id: str) -> models.Announcements:
    logger.info(f"GET: Announcement lookup requested: {id}")
    return db.query(models.Announcements).filter(models.Announcements.anid == id).first()

def getAnnouncementByDateAndSchool(db: Session, date: date, school: Optional[structs.SchoolName] = None) -> models.Announcements:
    if school is not None:
        logger.info(f"GET: Announcement lookup requested by date and school: {date} {school}")
        return (
            db.query(models.Announcements)
            .filter(models.Announcements.date == date, models.Announcements.school == school)
            .all()
        )
    else:
        logger.info(f"GET: Announcement lookup requested by only date: {date}")
        return (
            db.query(models.Announcements)
            .filter(models.Announcements.date == date)
            .all()
        )

def getAnnouncementsSlice(db: Session, top: int, bottom: int, school: Optional[structs.SchoolName] = None) -> List[models.Announcements]:
    if school is None:
        logger.info(f"GET: Announcement lookup requested for all schools")
        return db.query(models.Announcements).order_by(models.Announcements.date.desc()).slice(top, bottom).all()
    logger.info(f"GET: Announcement list requested by school {school}")
    return db.query(models.Announcements).order_by(models.Announcements.date.desc()).filter((models.Announcements.school == school) | (models.Announcements.school == None)).slice(top, bottom).all()

def getAnnouncementsByPage(db: Session, page: int, page_size: int, school: Optional[structs.SchoolName] = None) -> List[models.Announcements]:
    return getAnnouncementsSlice(db, page * page_size, (page + 1) * page_size, school)

def getSchedule(db: Session, user: schemas.UserReturn) -> Optional[List[models.Classes]]:
    if user.uid is not None:
        logger.info(f"GET: User schedule requested: {user.uid}")
        return (
            db.query(models.Classes)
            .filter(models.Classes.uid == user.uid)
            .all()
        )
    logger.error(f"GET: User schedule lookup failed: {user.uid}")
    return None

def getFriend(db: Session, friendship: schemas.FriendBase) -> Optional[models.Friends]:
    if friendship.user.uid is not None and friendship.friend.uid is not None:
        logger.info(f"GET: Friend lookup requested: {friendship.user.uid} --> {friendship.friend.uid}")
        return (
            db.query(models.Friends)
            .filter(models.Friends.uid == friendship.user.uid, models.Friends.fid == friendship.friend.uid)
            .first()
        )
    logger.error(f"GET: Friend lookup failed: {friendship.user.uid} {friendship.friend.uid}")
    return None

def getFriends(db: Session, user: schemas.UserReturn) -> Optional[List[models.Friends]]:
    if user.uid is not None:
        logger.info(f"GET: Friends lookup requested: {user.uid}")
        return db.query(models.Friends).filter(models.Friends.uid == user.uid).all()
    logger.error(f"GET: Friends lookup failed: {user.uid}")
    return None
    
def addSpecialDay(db: Session, specialDay: schemas.SpecialDay) -> bool:
    logger.info(f"ADD: Added special day: {specialDay.date}")
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
        logger.error(f"ADD: Special day addition failed: {e}")
        return False
    db.commit()
    return True


def addUser(db: Session, user: schemas.UserCreate) -> Optional[models.User]:
    if user.gid != None:  # Checks for GID as this is the only mandatory field.
        uid = str(uuid4())  # Generates UUID.
        (user.first, user.last) = prettifyName(user.first, user.last) # Prettifies name.
        userModel = models.User(
            uid=uid, **user.dict()
        )  # Creates model from dict of input values.
        db.add(userModel)
        db.commit()
        logger.info(
            f"ADD: User added by GID: {user.gid} Created UID: {uid}"
        )  # Logs the addition.
        return userModel  # Returns user details, import as many details are generated here.
    logger.error(f"ADD: User addition failed: {user.gid}")
    return None


def addClass(db: Session, newClass: schemas.Class) -> Optional[models.Classes]:
    if (
        newClass.tid is not None
        and newClass.uid is not None
        and newClass.block is not None
    ):  # Checks for the required fields.
        cid = secrets.token_hex(4)
        classModel = models.Classes(**newClass.dict(), cid=cid)  # Creates a model.
        db.add(classModel)  # Adds it.
        db.commit()
        logger.info(
            f"ADD: Class added: {cid} | TID: {newClass.tid} UID: {newClass.uid} Block: {newClass.block}"
        )  # Logs the addition.
        return classModel  # Returns class details.
    logger.error(
        f"ADD: Class addition failed | TID: {newClass.tid} UID: {newClass.uid} Block: {newClass.block}"
    )
    return None


def addTeacher(db: Session, newTeacher: schemas.TeacherCreate) -> Optional[models.Teacher]:
    if (
        newTeacher.first is not None
        and newTeacher.last is not None
        and newTeacher.school is not None
    ):  # Checks for required fields.
        tid = secrets.token_hex(4)  # Generates hexadecimal TID.
        newTeacher = prettifyTeacher(schemas.TeacherReturn(**newTeacher.dict(), tid=tid))
        teacherModel = models.Teacher(**newTeacher.dict())  # Creates a model.
        db.add(teacherModel)  # Adds teacher.
        db.commit()
        logger.info(
            f"ADD: Teacher added: {tid} | First: {newTeacher.first} Last: {newTeacher.last} School: {newTeacher.school}"
        )  # Logs the addition.
        return teacherModel
    logger.error(
        f"ADD: Teacher addition failed | First: {newTeacher.first} Last: {newTeacher.last} School: {newTeacher.school}"
    )
    return None


def addTeacherAlias(db: Session, newTeacherAlias: schemas.TeacherAliasCreate) -> Optional[models.Aliases]:

    (newTeacherAlias.first, newTeacherAlias.last) = prettifyName(newTeacherAlias.first, newTeacherAlias.last) # To ensure that all names are in the correct format.

    if newTeacherAlias.tid is None:
        logger.error(f"ADD: Teacher alias addition failed: {newTeacherAlias.tid}")
        return None
    if getTeacher(db, schemas.TeacherReturn(tid=newTeacherAlias.tid)) is None:
        logger.error(f"ADD: Teacher alias addition failed: {newTeacherAlias.tid}")
        return None
    
    alid = secrets.token_hex(4)
    teacherAlias = schemas.TeacherAliasReturn(**newTeacherAlias.dict(), alid=alid)
    teacherAliasModel = models.Aliases(**teacherAlias.dict())

    db.add(teacherAliasModel)
    db.commit()
    logger.info(f"ADD: Teacher alias added: {alid} | TID: {newTeacherAlias.tid}")
    return teacherAliasModel


def addAbsence(db: Session, absence: schemas.AbsenceCreate) -> Optional[models.Absences]:
    absence.teacher = schemas.TeacherCreate( **prettifyTeacher(absence.teacher).dict() ) # To ensure that all names that we work with are in the correct format.
    
    if (
        absence.teacher.first is None
        or
        absence.teacher.last is None
        or
        absence.teacher.school is None
    ):
        logger.error(f"ADD: Absence addition failed: {absence.teacher}")
        return None
    
    teacher = getTeacher(db, schemas.TeacherReturn(**absence.teacher.dict()))
    
    if teacher is None:
        print("Teacher not found. Going through aliases")
        # Teacher is not found, check if an alias exists.
        teacherAlias = getTeacherAlias(db, schemas.TeacherAliasBase(**absence.teacher.dict()))
        if teacherAlias is None:
            print("Teacher alias not found")
            teacher = addTeacher(db, absence.teacher)
        else:
            print("Teacher alias found")
            teacher = teacherAlias
    absenceModel = models.Absences(
        date=absence.date, tid=teacher.tid, note=absence.note, length=absence.length
    )
    db.add(absenceModel)
    db.commit()
    logger.info(f"ADD: Absence added: {absence.date} | TID: {teacher.tid}")
    return absenceModel


def addSession(db: Session, newSession: schemas.SessionCreate) -> Optional[models.UserSessions]:
    if newSession.uid is not None:  # Checks for required fields
        sessions = getSessionList(db, schemas.UserReturn(uid=newSession.uid))
        if sessions is None:
            logger.error(f"ADD: Session addition failed: {newSession.uid}")
            return None
        if len(sessions) >= 6:
            oldestSession = min(sessions, key=lambda t: t.last_accessed)
            removeSession(db, schemas.SessionReturn.from_orm(oldestSession))
        sid = secrets.token_hex(8)  # Generates SID.
        sessionModel = models.UserSessions(
            uid=newSession.uid, sid=sid, last_accessed=datetime.now()
        )  # Creates object including timestamp, makes model.
        db.add(sessionModel)  # Adds model.
        db.commit()
        logger.info(f"ADD: Session added {sid}.{newSession.uid}")  # Logs actions.
        return sessionModel
    logger.error(f"ADD: Session addition failed: {newSession.uid}")
    return None

def addAnnouncement(db: Session, announcement: schemas.AnnouncementBase) -> schemas.Bool:
    anid = secrets.token_hex(4)  # Generates hexadecimal TID.
    query = getAnnouncementByID(db, anid)

    while query is not None:
        anid = secrets.token_hex(4)
        query = getAnnouncementByID(db, anid)
        logger.info("ADD: Announcement ID already exists, generating new ID")
    
    announcementModel = models.Announcements(
            anid=anid,
            title=announcement.title,
            content=announcement.content,
            date=announcement.date,
            school=announcement.school,
        )
    db.add(announcementModel)

    db.commit()
    logger.info(f"ADD: Announcement added: {anid}")
    # Rework so it doesn't return a bool.
    return schemas.Bool(success=True)

def addFriend(db: Session, friendship: schemas.FriendCreate) -> Optional[models.Friends]:
    # Search user up in the database.
    searched_user = getUser(db, schemas.UserReturn(uid=friendship.user.uid))
    searched_friend = getUser(db, schemas.UserReturn(uid=friendship.friend.uid))

    # Validate that the user exists in the database.
    if searched_user is None or searched_friend is None:
        logger.error(f"ADD: Friend addition failed: {searched_user} --({friendship.status})--> {searched_friend}. User or Friend not found.")
        return None
    if friendship.user.uid == friendship.friend.uid:
        logger.error(f"ADD: Friend addition failed: {searched_user.uid} --({friendship.status})--> {searched_friend.uid}. Friend and User cannot be the same person.")
        return None
    
    success: schemas.Bool = schemas.Bool(success=True)

    # Check if entry already exists.
    if getFriend(db, friendship) is None:
        # Add entry to database.
        friendship_entry = models.Friends(
                uid=friendship.user.uid,
                fid=friendship.friend.uid,
                date=friendship.date,
                status=friendship.status
            )
        db.add(friendship_entry)
        db.commit()
        logger.info(f"ADD: Friend added: {searched_user.uid} --({friendship.status})--> {searched_friend.uid}")
        return friendship_entry
    else:
        logger.error(f"ADD: Friend addition failed: {searched_user.uid} --({friendship.status})--> {searched_friend.uid}. User to Friend already exists.")
        return None

def addCanceled(db: Session, canceled: schemas.Canceled) -> Optional[models.Canceled]:
    # Search user up in the database.
    searched_user = getUser(db, schemas.UserReturn(uid=canceled.cls.uid))

    # Validate that the user exists in the database.
    if searched_user is None:
        logger.error(f"ADD: Canceled addition failed: {searched_user}")
        return None

    class_entry = getClass(db, canceled.cls)

    if class_entry is None:
        logger.error(f"ADD: Canceled addition failed: {searched_user}")
        return None
    
    # Check if entry already exists.
    if getCanceled(db, canceled) is None:
        # Add entry to database.
        canceled_entry = models.Canceled(
                date=canceled.date,
                cid=class_entry.cid,
            )
        db.add(canceled_entry)
        db.commit()
        logger.info(f"ADD: Canceled added: {searched_user.uid}")
        return canceled_entry
    else:
        logger.error(f"ADD: Canceled addition failed: {searched_user.uid}")
        return None

def removeSession(db: Session, session: schemas.SessionReturn) -> bool:
    if session.sid is not None and session.uid is not None:
        db.query(models.UserSessions).filter(
            models.UserSessions.uid == session.uid, models.UserSessions.sid == session.sid
        ).delete()
        db.commit()
        logger.info(f"REMOVE: Removed session: {session.sid}.{session.uid}")
        return True
    logger.error(f"REMOVE: Session removal failed: {session.sid}")
    return False


def removeUser(db, user: schemas.UserReturn) -> bool:
    if user.uid is not None:  # Checks for required fields.
        # self.removeClassesByUser(user) # Removes all of a user's classes.
        db.query(models.User).filter(
            models.User.uid == user.uid
        ).delete()  # Removes the user.
        db.commit()
        logger.info(f"REMOVE: Student removed: {user.uid}")  # Logs the action.
        return True
    logger.error(f"REMOVE: Student removal failed: {user.uid}")
    return False


def removeClass(db, cls: schemas.Class) -> bool:
    if (
        cls.tid is not None and cls.uid is not None and cls.block is not None
    ):  # Checks for required fields.
        modelClass = models.Classes(**cls.dict())  # Builds model.
        db.delete(modelClass)  # Removes it.
        db.commit()
        logger.info(
            f"REMOVE: Class removed: TID: {cls.tid} UID: {cls.uid} Block: {cls.block}"
        )  # Logs the action.
        return True
    logger.error(
        f"REMOVE: Class removal failed: TID: {cls.tid} UID: {cls.uid} Block: {cls.block}"
    )
    return False


def removeSpecialDay(db, date: date) -> bool:
    logger.info(f"REMOVE: Special day removed: {date}")
    try:
        db.query(models.SpecialDays).filter(models.SpecialDays.date == date).delete()
    except Exception as e:
        logger.error(f"REMOVE: Special day removal failed: {e}")
        return False
    return True


def removeClassesByUser(
    db, user: schemas.UserReturn
) -> bool:  # Used for updating schedule and cancellation.
    classes: Optional[List[models.Classes]] = getClassesByUser(db, user)  # Gets a student's classes.
    if classes is None:
        return False
    for cls in classes:
        db.delete(cls)  # Deletes them all.
        logger.info(f"REMOVE: Class removed: TID: {cls.tid} UID: {cls.uid} Block: {cls.block}")
    db.commit()
    logger.info(f"REMOVE: Finished removing all classes for UID: {user.uid}")  # Logs the action.
    return True


def removeAbsencesByDate(db, date: datetime) -> bool:
    db.query(models.Absences).filter(models.Absences.date == date).delete()
    db.commit()
    logger.info(f"REMOVE: Removed absences for date: {str(date)}")
    return True

def removeAnnouncement(db, announcement: schemas.AnnouncementReturn) -> bool:
    if announcement is None:
        return False
    if announcement.anid is None:
        logger.error(f"REMOVE: Announcement removal failed: {announcement.anid}")
        return False
    db.query(models.Announcements).filter(models.Announcements.anid == announcement.anid).delete()
    db.commit()
    logger.info(f"REMOVE: Removed announcement: {announcement.anid}")
    return True

def removeFriend(db, friendship: schemas.FriendReturn) -> bool:
    if friendship is None:
        return False
    if friendship.user.uid is None or friendship.friend.uid is None:
        logger.error(f"REMOVE: Friend removal failed: {friendship.user.uid} -> {friendship.friend.uid}")
        return False
    db.query(models.Friends).filter(
        models.Friends.uid == friendship.user.uid, models.Friends.fid == friendship.friend.uid
    ).delete()
    db.commit()
    logger.info(f"REMOVE: Removed friendship: {friendship.user.uid} -> {friendship.friend.uid}")
    return True

def updateSchedule(db, user: schemas.UserReturn, schedule: schemas.Schedule) -> bool:
    if user.school is None:
        searched_user: Optional[models.User] = getUser(db, user)
        if searched_user is None:
            logger.error(f"UPDATE: Schedule update failed: {user.uid}. User not found.")
            return False
        if searched_user.school is None:
            logger.error(f"UPDATE: Updating schedule failed: {user.uid} has no school.")
            return False

    if user.uid is not None:
        removeClassesByUser(db, user)  # Removes all old classes.
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
                        addedTeacher = addTeacher(db,
                            schemas.TeacherCreate(
                                first=teacher.first,
                                last=teacher.last,
                                school=user.school,
                            ),
                        )
                        if addedTeacher is None:
                            logger.error(f"UPDATE: Updating schedule failed: {teacher.first} {teacher.last} failed to be added. Should never occur.")
                            return False
                        tid = addedTeacher.tid  # Adds them to DB if they don't exist.
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
        logger.info(f"UPDATE: Schedule update successful for UID: {user.uid}")
        return True
    logger.error("UPDATE: Schedule update failed. No UID provided.")
    return False


def updateProfile(db, profile: schemas.UserBase, uid: str) -> models.User:
    result = db.execute(
        update(models.User)
        .where(models.User.uid == uid)
        .values(**profile.dict())
        .execution_options(synchronize_session="fetch")
    )
    db.commit()
    logger.info(f"UPDATE: Profile updated: {uid}")
    return result  # Returns new profile.


def updateUserSettings(db, settings: schemas.UserSettings, uid: str) -> bool:
    db.query(models.UserSettings).where(models.UserSettings.uid == uid).delete()
    settingsModel = models.UserSettings(**settings.dict())
    settingsModel.uid = uid
    db.add(settingsModel)
    db.commit()
    logger.info(f"UPDATE: User settings updated: {uid}")
    return True


def updateFCMToken(db, token: schemas.Token, uid: str, sid: str) -> models.UserSessions:
    result = db.execute(
        update(models.UserSessions)
        .where(models.UserSessions.uid == uid, models.UserSessions.sid == sid)
        .values(fcm_token=token.token, fcm_timestamp=datetime.now())
        .execution_options(synchronize_session="fetch")
    )
    db.commit()
    logger.info(f"UPDATE: FCM Token: {sid}.{uid}")
    return result


def updateAnnouncement(db, updateAnnouncement: schemas.AnnouncementUpdate) -> schemas.Bool:
    if updateAnnouncement.anid is None:
        logger.error(f"UPDATE: Announcement update failed: {updateAnnouncement.anid}")
        return False
    
    result = db.execute(
        update(models.Announcements)
        .where(models.Announcements.anid == updateAnnouncement.anid)
        .values(
            title = updateAnnouncement.title,
            content = updateAnnouncement.content,
            school = updateAnnouncement.school,
        )
    )
    db.commit()
    logger.info(f"UPDATE: Announcement updated: {updateAnnouncement.anid}")
    return schemas.Bool(success=True)
    
def updateSpecialDay(db, updateSpecialDay: schemas.SpecialDay) -> schemas.Bool:
    if updateSpecialDay.date is None:
        logger.error(f"UPDATE: Special day update failed: {updateSpecialDay.date}")
        return schemas.Bool(success=False)
    if getSpecialDay(db, updateSpecialDay.date) is not None:
        result = db.execute(
            update(models.SpecialDays)
            .where(models.SpecialDays.date == updateSpecialDay.date)
            .values(
                name = updateSpecialDay.name,
                schedule = updateSpecialDay.schedule,
                note = updateSpecialDay.note,
            )
        )
        db.commit()
        logger.info(f"UPDATE: Special day updated: {updateSpecialDay.date}")
        return schemas.Bool(success=True)
    logger.error(f"UPDATE: Special day update failed: {updateSpecialDay.date} Date does not exist")
    return schemas.Bool(success=False)

def updateFriendStatus(db, friendship: schemas.FriendBase, status: structs.FriendshipStatus) -> schemas.Bool:
    oldEntry = getFriend(db, friendship)

    print(f"Old entry: {oldEntry} | {oldEntry.status}")
    if oldEntry is None:
        logger.error(f"UPDATE: Friend status update failed: {friendship.user.uid} -> {friendship.friend.uid}. Could not find friendship.")
        return schemas.Bool(success=False)
    
    oldStatus = oldEntry.status

    result = db.execute(
                    update(models.Friends)
                    .where(models.Friends.uid == friendship.user.uid, models.Friends.fid == friendship.friend.uid)
                    .values(status=status)
                    )
    db.commit()

    logger.info(f"UPDATE: Friend status updated: {friendship.user.uid} -> {friendship.friend.uid}. {oldStatus} -> {status}")
    return schemas.Bool(success=True)
    
def reset(db):
    print("INTERNAL FLAG: RESETTING DB!")
    db.query(models.User).delete()
    db.query(models.Teacher).delete()
    db.query(models.Classes).delete()
    db.query(models.Absences).delete()
    db.query(models.UserSessions).delete()
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
        logger.info(
            f"CHECK: Checked onboarding for: {uid} {gid}. User does not exist in users table."
        )
        return False, False

    # If user is in the table, check if they have any classes.
    resClasses: Optional[List[models.Classes]] = getClassesByUser(db, resUser)

    if resClasses is None:
        logger.info(f"CHECK: Checked onboarding for: {uid} {gid}. User exists in users table, but does not have any classes.")
        return True, False
    
    if len(resClasses) == 0:  # Lack of classes means they have not been onboarded fully
        logger.info(
            f"CHECK: Checked onboarding for: {resUser.uid}. User has not been onboarded."
        )
        return True, False
    else:
        logger.info(
            f"CHECK: Checked onboarding for: {resUser.uid}. User has been onboarded."
        )
        return True, True  # If they have classes, they have been onboarded!
