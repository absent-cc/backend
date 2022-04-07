import firebase_admin
from firebase_admin import messaging, credentials
from ..dataTypes import structs
from loguru import logger

cred = credentials.Certificate("creds/firebase.json")
firebase = firebase_admin.initialize_app(cred)
APN_HEADERS = {
    "apns_priority": "10",
}


def sendMessage(message):
    notification = messaging.Notification(
        title=message.title,
        body=message.body,
    )

    message = messaging.Message(
        notification=notification,
        token=message.token,
        android=messaging.AndroidConfig(priority="high"),
        apns=messaging.APNSConfig(headers=APN_HEADERS),
    )

    response = messaging.send(message)
    logger.info(f"Notification sent: {response}")
    return response


TOKEN = "frdpfVydRWmZiSWMJpq09g:APA91bEhOPsiXVmqHOCcIaj9Xpld-rDBwR26FRvI1tAgivdSHgT1QYBORbOc4oE39DPZ6Vw3EtHC4qdJWAv5ZPySfwg4ZY9nKND5QS2Gy2_6AC97Fbna_INOgiKCBAes_re4kaFlUpS_"
