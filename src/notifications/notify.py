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
        notifDict = {}

        validBlocks = structs.SchoolBlocksOnDay()[self.date.weekday()]
        absences = crud.getAbsenceList(self.db, self.date, self.school)
        for absence in absences:
            for block in validBlocks:
                classes = absence.teacher.classes
                for cls in classes:
                    notifDict[cls.uid] = True
        
        return notifDict

    def buildMessage(self, user, content: str):
        userMessages = []
        for session in user.sessions:
            notification = messaging.Notification(
                title="Absence list notification.",
                body=content,
            )

            message = messaging.Message(
                notification=notification,
                token=session.fcm_token,
                android=messaging.AndroidConfig(priority="high"),
                apns=messaging.APNSConfig(headers=self.APN_HEADERS)
            )

            userMessages.append(message)
        return userMessages

    def buildMessages(self):
        notifDict = self.calculateAbsences()
        messages = []
        for user in crud.getUsersBySchool(self.db, self.school):
            if user.settings[0].notify and user.uid in notifDict:
                for message in self.buildMessage(user, "Hey there! You have absent teachers. Click this notification for more info."):
                    messages.append(message)
            elif user.settings[0].notifyWhenNone:
                for message in self.buildMessage(user, "The absence list has been posted. Check it out!"):
                    messages.append(message)
        return messages

    def sendMessages(self):

        messages = self.buildMessages()

        for message in messages:
            try:
                response = messaging.send(message)
                logger.info(f"Notification sent: {response}")
            except:
                logger.info("Message failed to send")

if __name__ == "__main__":
    test = Notify(structs.SchoolName.NEWTON_NORTH, datetime.date.today())
    print(test.sendMessages(test.buildMessages()))
            
