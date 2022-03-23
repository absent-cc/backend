from src.database.database import SessionLocal
from ..dataTypes import structs, models, schemas
import datetime
from ..database import crud

from firebase_admin import messaging, credentials
from typing import Optional, List, Tuple
from loguru import logger

class Notify:
    def __init__(self, school: structs.SchoolName, date: datetime.date = datetime.date.today()):

        self.db = SessionLocal()
        self.school = school
        self.date = date
        self.absences: Optional[List[models.Absence]] = crud.getAbsenceList(self.db, self.date, self.school)

        self.APN_HEADERS = {
        "apns_priority": "10",
        }

    def calculateAbsences(self):

        hasAbsentTeacher = set()
        alwaysNotify = set()

        validBlocks = structs.SchoolBlocksOnDay()[self.date.weekday()]
        absences = crud.getAbsenceList(self.db, self.date, self.school)
       
        for absence in absences:
            for block in validBlocks:
                classes = absence.teacher.classes
                for _class in classes:
                    if _class.user.settings[0].notify: # Add the people with absent teachers.
                        for session in _class.user.sessions:
                            print(session.fcm_token)
                            if session.fcm_token != None and (bool(session.fcm_token) and bool(session.fcm_token.strip())) != False:
                                hasAbsentTeacher.add(session.fcm_token)
                    # elif _class.user.settings[0].notifyWhenNone: # Add the always notify people
                    #     for session in _class.user.sessions:
                    #         if session.fcm_token != None and (bool(session.fcm_token) and bool(session.fcm_token.strip())) != False:
                    #             alwaysNotify.add(session.fcm_token)
        
        alwaysNotifyUsers = crud.getAlwaysNotify(self.db)

        for notifyEntry in alwaysNotifyUsers:
            user = notifyEntry.user
            for session in user.sessions:
                print(session.fcm_token)
                if session.fcm_token != None and (bool(session.fcm_token) and bool(session.fcm_token.strip())) != False:
                    alwaysNotify.add(session.fcm_token)
            
        return hasAbsentTeacher, alwaysNotify

    def sendMessages(self):

        hasAbsentTeacherSet, alwaysNotifySet = self.calculateAbsences()

        hasAbsentTeacher = list(hasAbsentTeacherSet)
        alwaysNotify = list(alwaysNotifySet)
        print(hasAbsentTeacherSet, alwaysNotifySet)
        del hasAbsentTeacherSet
        del alwaysNotifySet

        hasAbsentTeacher = [hasAbsentTeacher[i:i + 500] for i in range(0, len(hasAbsentTeacher), 500)]
        alwaysNotify = [alwaysNotify[i:i + 500] for i in range(0, len(alwaysNotify), 500)]

        # Notify the people with absent teachers.

        multicastMessages = []
        for chunk in hasAbsentTeacher:
            msg = messaging.MulticastMessage(
                tokens = chunk,
                notification = messaging.Notification(
                    title="Your teacher is abSENT",
                    body="Hey there! You have an absent teacher today. Click me to learn more."
                ),
                android = messaging.AndroidConfig(priority="high"),
                apns = messaging.APNSConfig(headers=self.APN_HEADERS)
            )
            multicastMessages.append(msg)

        # Notify the always notify people.

        for chunk in alwaysNotify:
            msg = messaging.MulticastMessage(
                tokens = chunk,
                notification = messaging.Notification(
                    title="abSENT List Posted",
                    body="Hey there! Today's absent list has been posted. Click me to view."
                ),
                android = messaging.AndroidConfig(priority="high"),
                apns = messaging.APNSConfig(headers=self.APN_HEADERS)
            )
            multicastMessages.append(msg)

        for message in multicastMessages:
            response = messaging.send_multicast(message)
            logger.info(f"Notifications for {self.school} sent. Number sent: {len(hasAbsentTeacher) + len(alwaysNotify)} in {len(multicastMessages)} multicasts. Number of failures: {response.failure_count}")

        return True
