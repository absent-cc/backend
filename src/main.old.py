import threading, time, yaml
from .dataTypes import structs
from schoology.schoologyListener import *
from database.database import *
from datetime import timedelta, datetime, timezone

# Open files.
with open("secrets.yml") as f:
    cfg = yaml.safe_load(f)

# Define API variables.
SCHOOLOGYCREDS = structs.SchoologyCreds(
    {
        structs.SchoolName.NEWTON_NORTH: cfg["north"]["key"],
        structs.SchoolName.NEWTON_SOUTH: cfg["south"]["key"],
    },
    {
        structs.SchoolName.NEWTON_NORTH: cfg["north"]["secret"],
        structs.SchoolName.NEWTON_SOUTH: cfg["south"]["secret"],
    },
)

# Make threads regenerate on fault.
def threadwrapper(func):
    def wrapper():
        while True:
            try:
                func()
            except BaseException as error:
                print("abSENT - {!r}; restarting thread".format(error))
            else:
                print("abSENT - Exited normally, bad thread, restarting")

    return wrapper


# Listen for Schoology updates.
def sc_listener():
    saturday = 5
    sunday = 6
    holidays = []

    # debug mode
    debugMode = True

    dailyCheckTimeStart = 7  # hour
    dailyCheckTimeEnd = 12  # hour

    resetTimeOne = (0, 0)  # midnight
    resetTimeTwo = (4, 20)  # midnight

    schoologySuccessCheck = False
    dayoffLatch = False
    while True:
        currentTime = datetime.now(timezone.utc) - timedelta(
            hours=5
        )  # Shift by 5 hours to get into EST.
        currentDate = currentTime.strftime("%d/%m/%Y")
        dayOfTheWeek = currentTime.weekday()

        print("LISTENING", currentTime)

        if (
            dayOfTheWeek == saturday
            or dayOfTheWeek == sunday
            or currentDate in holidays
        ) and not debugMode:
            if dayoffLatch == False:
                print("abSENT DAY OFF")
                dayoffLatch = True
        else:
            aboveStartTime: bool = currentTime.hour >= dailyCheckTimeStart
            belowEndTime: bool = currentTime.hour <= dailyCheckTimeEnd
            if (
                aboveStartTime and belowEndTime and not schoologySuccessCheck
            ) or debugMode:
                print("CHECKING SCHOOLOGY.")
                sc = SchoologyListener(SCHOOLOGYCREDS)
                schoologySuccessCheck = sc.run()
                print("CHECK COMPLETE.")

        if currentTime.hour == resetTime[0] or currentTime.hour == resetTime[0]:
            # Reset schoologySuccessCheck to false @ midnight
            # Only change value when it is latched (true)
            if schoologySuccessCheck == True:
                print("RESTART")
                dayoffLatch = False
                schoologySuccessCheck = False

        time.sleep(15)  # Sleep for 15 seconds.


# # Configure and start threads.
# threads = {
#         'sc': threading.Thread(target=threadwrapper(sc_listener), name='sc listener'),
# }

threads["sc"].daemon = True
threads["sc"].start()
print(threads["sc"].isDaemon())
# sc_listener()
