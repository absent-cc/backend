import logging
import time

import firebase_admin
from firebase_admin import credentials

from .dataTypes import tools
from .schoology.schoologyListener import *
from .dataTypes import structs

# Get secrets info from config.ini
config_path = "config.ini"
south_key = tools.read_config(config_path, "NSHS", "key")
south_secret = tools.read_config(config_path, "NSHS", "secret")
north_key = tools.read_config(config_path, "NNHS", "key")
north_secret = tools.read_config(config_path, "NNHS", "secret")

# Define API variables.
SCHOOLOGYCREDS = structs.SchoologyCreds(
    {
        structs.SchoolName.NEWTON_NORTH: north_key,
        structs.SchoolName.NEWTON_SOUTH: south_key,
    },
    {
        structs.SchoolName.NEWTON_NORTH: north_secret,
        structs.SchoolName.NEWTON_SOUTH: south_secret,
    },
)

# Listen for Schoology updates.
def listener():
    saturday = 5
    sunday = 6
    # debug mode
    debugMode = False
    # debugMode = True

    dailyCheckTimeStart = 7  # hour. Default: 7
    dailyCheckTimeEnd = 12  # hour. Default: 11

    resetTimeOne = (0, 0)  # Midnight
    resetTimeTwo = (4, 20)  # Light It Up

    southCheck: bool = False
    northCheck: bool = False
    dayoffLatch = False

    while True:
        currentTime = datetime.now(timezone.utc) - timedelta(
            hours=5
        )  # Shift by 5 hours to get into EST.

        holiday: bool = False

        dayOfTheWeek = currentTime.weekday()

        if not dayoffLatch:
            logger.info(f"Listening: {currentTime}")
            logger.info(f"Schoology success: NSHS: {southCheck}, NNHS: {northCheck}.")

            db = SessionLocal()

            holidayCheck = crud.getSpecialDay(db, date=currentTime.date())

            if holidayCheck is not None:
                if (
                    len(holidayCheck.schedule) == 0
                ):  # If there is no schedule, it's a holiday. Remember that length property is defined in ScheduleWithTimes class.
                    holiday = True
                    logger.info(f"Today is a holiday: {holidayCheck.name}")
                else:
                    logger.info(f"Unique schedule for today, not a holiday")

            if (
                dayOfTheWeek == saturday or dayOfTheWeek == sunday or holiday
            ) and not debugMode:
                if not dayoffLatch:
                    logger.info(
                        f"Day off. Latching to sleep! Day Number: {dayOfTheWeek}"
                    )
                    dayoffLatch = True
            else:
                aboveStartTime: bool = currentTime.hour >= dailyCheckTimeStart
                belowEndTime: bool = currentTime.hour <= dailyCheckTimeEnd
                if (
                    aboveStartTime and belowEndTime
                ) or debugMode:  # If its during the check time and schoology hasn't already been checked.
                    logger.info("Polling schoology...")
                    sc = SchoologyListener(SCHOOLOGYCREDS)

                    if not southCheck:
                        southCheck = sc.southRun()
                    else:
                        logger.info("South has already been checked today.")

                    if not northCheck:
                        northCheck = sc.northRun()
                    else:
                        logger.info("North has already been checked today.")
                    
                    logger.info(f"Schoology success: NSHS: {southCheck}, NNHS: {northCheck}.")
                else:
                    if southCheck and northCheck:
                        logger.info(
                            "Skipping check, already have absence list for today"
                        )
                    if not (aboveStartTime and belowEndTime):
                        logger.info("Skipping check, outside of bounds")

        if currentTime.hour == resetTimeOne[0] or currentTime.hour == resetTimeTwo[0]:
            # Reset schoologySuccessCheck to false @ midnight
            # Only change value when it is latched (true)
            logger.info("Resetting state for the new day")
            dayoffLatch = False
            southCheck = False
            northCheck = False

        logger.info(f"Notify call times: {Notify.NUMBER_OF_CALLS}")
        time.sleep(15)  # Sleep for 15 seconds.


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


if __name__ == "__main__":
    cred = credentials.Certificate("creds/firebase.json")
    firebase = firebase_admin.initialize_app(cred)

    # Add logging
    logger.add("logs/listener/latest.log", rotation="4 hours", retention=0)

    logger.add(
        "logs/listener/{time:YYYY-MM-DD}/schoology.log",
        enqueue=True,
        filter="src.schoology",
        rotation="00:00",
        retention=12,
        compression="tar.gz",
    )
    logger.add(
        "logs/listener/{time:YYYY-MM-DD}/database.log",
        enqueue=True,
        filter="src.database",
        rotation="00:00",
        retention=12,
        compression="tar.gz",
    )
    logger.add(
        "logs/listener/{time:YYYY-MM-DD}/notifications.log",
        enqueue=True,
        filter="src.notifications",
        rotation="00:00",
        retention=12,
        compression="tar.gz",
    )

    listener()
