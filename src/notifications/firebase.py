import firebase_admin
from firebase_admin import messaging


class NotificationsDriver:
    def __init__(self):
        self.TITLE = "abSENT: cancelled class notification"
        self.IMAGE_URL = None
        self.firebase = firebase_admin.initialize_app()

    def sendMessage(self, token: str, content: str):
        notification = messaging.Notification(
            title=self.TITLE,
            body=content,
            image=sef.IMAGE_URL
        )

        message = messaging.Message(
            notification=notification,
            token=token
        )

        response = messaging.send(message)
        return response

TOKEN = "frdpfVydRWmZiSWMJpq09g:APA91bEhOPsiXVmqHOCcIaj9Xpld-rDBwR26FRvI1tAgivdSHgT1QYBORbOc4oE39DPZ6Vw3EtHC4qdJWAv5ZPySfwg4ZY9nKND5QS2Gy2_6AC97Fbna_INOgiKCBAes_re4kaFlUpS_"
        
