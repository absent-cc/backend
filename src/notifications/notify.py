import datetime
from typing import Optional, List

from firebase_admin import messaging
from loguru import logger

from src.database.database import SessionLocal
from ..dataTypes import structs, models
from ..database import crud


class Notify:

    # REMOVE ME LATER
    NUMBER_OF_CALLS: int = 0
    # REMOVE ME LATER

    def __init__(
        self, school: structs.SchoolName, date: datetime.date = datetime.date.today()
    ):

        self.db = SessionLocal()
        self.school = school
        self.date = date
        self.absences: Optional[List[models.Absence]] = crud.getAbsenceList(
            self.db, self.date, self.school
        )

        self.APN_HEADERS = {
            "apns_priority": "10",
        }

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
                        if cls.user.settings[
                            0
                        ].notify:  # Add the people with absent teachers.
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

        alwaysNotifyUsers = crud.getAlwaysNotify(self.db, self.school)

        for notifyEntry in alwaysNotifyUsers:
            user = notifyEntry.user
            for session in user.sessions:
                print(session.fcm_token)
                if (
                    session.fcm_token is not None
                    and len(session.fcm_token.strip()) != 0
                    and (bool(session.fcm_token) and bool(session.fcm_token.strip()))
                    != False
                ):
                    # Check if not None, not empty str, and if it does not contain a leading whitespace (which breaks stuff)
                    alwaysNotify.add(session.fcm_token)
        return hasAbsentTeacher, alwaysNotify

    def sendMessages(self):

        hasAbsentTeacherSet, alwaysNotifySet = self.calculateAbsences()

        hasAbsentTeacher = list(hasAbsentTeacherSet)
        alwaysNotify = list(alwaysNotifySet)

        del hasAbsentTeacherSet
        del alwaysNotifySet

        hasAbsentTeacher = [
            hasAbsentTeacher[i : (i + 500)]
            for i in range(0, len(hasAbsentTeacher), 500)
        ]
        alwaysNotify = [
            alwaysNotify[i : (i + 500)] for i in range(0, len(alwaysNotify), 500)
        ]

        # Notify the people with absent teachers.

        multicastMessages = []
        for fcm_token in hasAbsentTeacher:
            msg = messaging.MulticastMessage(
                tokens=fcm_token,
                notification=messaging.Notification(
                    title="Your teacher is abSENT",
                    body="Hey there! You have an absent teacher today. Click me to learn more.",
                ),
                android=messaging.AndroidConfig(priority="high"),
                apns=messaging.APNSConfig(headers=self.APN_HEADERS),
            )
            multicastMessages.append(msg)

        # Notify the always notify people.

        for fcm_token in alwaysNotify:
            msg = messaging.MulticastMessage(
                tokens=fcm_token,
                notification=messaging.Notification(
                    title="abSENT List Posted",
                    body="Hey there! Today's absent list has been posted. Click me to view.",
                ),
                android=messaging.AndroidConfig(priority="high"),
                apns=messaging.APNSConfig(headers=self.APN_HEADERS),
            )
            multicastMessages.append(msg)

        for message in multicastMessages:
            response = messaging.send_multicast(message)
            logger.info(
                f"Notifications for {self.school} sent. Number of failures: {response.failure_count}"
            )

        Notify.NUMBER_OF_CALLS += 1
        return True


if __name__ == "__main__":
    test = Notify(structs.SchoolName.NEWTON_SOUTH)
    print(test.calculateAbsences())
