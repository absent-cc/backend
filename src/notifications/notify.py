import datetime
from typing import Dict, Optional, List, Tuple

from firebase_admin import messaging
from loguru import logger

from src.database.database import SessionLocal
from ..dataTypes import structs, models # type: ignore
from ..database import crud # type: ignore


class Notify:
    def __init__(
        self, school: structs.SchoolName, date: datetime.date # REPLACE ME WHEN RUNNING
        # self, school: structs.SchoolName, date: datetime.date = datetime.date.today()
    ):

        self.db = SessionLocal()
        self.school = school
        self.date = date
        self.absences: Optional[List[models.Absences]] = crud.getAbsenceList(
            self.db, self.date, self.school
        )

        self.APN_HEADERS = {
            "apns_priority": "10",
        }

    def calculateAbsencesNew(self) -> Dict[Tuple[models.Teacher, structs.SchoolBlock], List[models.User]]:
        canceleds: List[models.Canceled] = crud.getCanceledsBySchool(self.db, self.school, self.date)
        absentGroups: Dict[Tuple[models.Teacher, structs.SchoolBlock], List[models.User]] = {}

        for canceled in canceleds:
            teacher = canceled.cls.teacher
            block = canceled.cls.block
            if (teacher, block) not in absentGroups:
                absentGroups[(teacher, block)] = [canceled.cls.user]
            else:
                absentGroups[(teacher, block)].append(canceled.cls.user)

        return absentGroups

    def calculateAbsences(self):

        hasAbsentTeacher = set()
        alwaysNotify = set()

        validBlocks = structs.SchoolBlocksOnDayWithTimes()[self.date.weekday()].blocks()
        # validBlocks = structs.SchoolBlocksOnDay()[self.date.weekday()]
        absences = crud.getAbsenceList(self.db, self.date, self.school)

        for absence in absences:
            for block in validBlocks:
                classes = [cls for cls in absence.teacher.classes if cls.block == block]
                for cls in classes:
                    try:
                        if cls.user.settings[0].notify:  # Add the people with absent teachers.
                            for session in cls.user.sessions:
                                if (
                                    session.fcm_token is not None
                                    and len(session.fcm_token.strip()) != 0
                                    and (
                                        bool(session.fcm_token)
                                        and bool(session.fcm_token.strip())
                                    )
                                    != False
                                ):
                                    # Check if not None, not empty str, and if it does not contain a leading whitespace (which breaks stuff)
                                    hasAbsentTeacher.add(session.fcm_token)
                                else:
                                    logger.info(
                                        f"{cls.user} has invalid FCM token formats"
                                    )
                    except Exception as e:
                        logger.error(f"{cls.user} has invalid FCM token formats")
                        logger.error(e)

        alwaysNotifyUsers: List[models.User] = crud.getAlwaysNotify(self.db, self.school)

        for notifyEntry in alwaysNotifyUsers:
            user = notifyEntry.user
            for session in user.sessions:
                if (
                    session.fcm_token is not None
                    and len(session.fcm_token.strip()) != 0
                    and (bool(session.fcm_token) and bool(session.fcm_token.strip()))
                    != False
                ):
                    # Check if not None, not empty str, and if it does not contain a leading whitespace (which breaks stuff)
                    alwaysNotify.add(session.fcm_token)
        return hasAbsentTeacher, alwaysNotify

    def validateFCMToken(self, token: str) -> bool:
        return token is not None and len(token.strip()) != 0 and (bool(token) and bool(token.strip())) != False
    
    def prepareAlwaysNotify(self) -> List[str]:
        alwaysNotify = crud.getAlwaysNotify(self.db, self.school)
        allTokens = []

        for notifyEntry in alwaysNotify:
            user = notifyEntry.user
            for session in user.sessions:
                if self.validateFCMToken(session.fcm_token):
                    allTokens.append(session.fcm_token)
        return allTokens

    def prepareAbsentTeacher(self) -> Dict[Tuple[models.Teacher, structs.SchoolBlock], List[str]]:
        absentGroups: Dict[Tuple[models.Teacher, structs.SchoolBlock], List[models.User]]= self.calculateAbsencesNew()

        # Maps
        fcmTokenByTeacher: Dict[Tuple[models.Teacher, structs.SchoolBlock], List[str]] = {}

        for teacher_block, users in absentGroups.items():
            total_fcm_tokens: List[str] = []
            # Get all the FCM tokens for the teacher and block
            for user in users:
                if len(user.sessions) == 0:
                    logger.error(f"{user} has no sessions")
                    continue
                for session in user.sessions:
                    if self.validateFCMToken(session.fcm_token):
                        total_fcm_tokens.append(session.fcm_token)
                    else:
                        logger.error(f"{user} has invalid FCM token formats") 
            
            # Add the FCM tokens to the dictionary
            if teacher_block not in fcmTokenByTeacher:
                fcmTokenByTeacher[teacher_block] = total_fcm_tokens
        
        return fcmTokenByTeacher
        
    def sendMessages(self):
        fcmTokensByTeacher: Dict[Tuple[models.Teacher, structs.SchoolBlock], List[str]] = self.prepareAbsentTeacher()

        alwaysNotify: List[str] = self.prepareAlwaysNotify()

        # Notify the people with absent teachers.
        multicastMessages = []

        for teacher_block, fcm_tokens in fcmTokensByTeacher.items():
            for i in range(0, len(fcm_tokens), 500):
                chunked_tokens = fcm_tokens[i : i + 500]
                title = f"{teacher_block[1]}: {teacher_block[0].first} {teacher_block[0].last}"
                absentEntry = crud.getAbsenceByTeacherAndDate(self.db, teacher_block[0], self.date)
                if absentEntry is None:
                    body = "Cancelled Class! Click me to see details!"
                else:
                    body = f"Duration: {absentEntry.length} | Note: {absentEntry.note}"
                msg = messaging.MulticastMessage(
                    tokens=chunked_tokens,
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    android=messaging.AndroidConfig(priority="high"),
                    apns=messaging.APNSConfig(headers=self.APN_HEADERS),
                )
                multicastMessages.append(msg)

        # Notify the always notify people.
        for i in range(0, len(alwaysNotify), 500):
            chunked_always_notify = alwaysNotify[i : i + 500]
            msg = messaging.MulticastMessage(
                tokens=chunked_always_notify,
                notification=messaging.Notification(
                    title="abSENT List Posted",
                    body="Hey there! Today's absent list has been posted. Click me to view.",
                ),
                android=messaging.AndroidConfig(priority="high"),
                apns=messaging.APNSConfig(headers=self.APN_HEADERS),
            )
            multicastMessages.append(msg)

        logger.info(f"Sending {len(multicastMessages)} Firebase notification messages")
        for message in multicastMessages:
            response = messaging.send_multicast(message)
            logger.info(
                f"Notifications for {self.school} sent. Number of failures: {response.failure_count}"
            )
 
        return True