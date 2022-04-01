import configparser
import threading, time, yaml
from loguru import logger
from .dataTypes import structs, tools
from .schoology.schoologyListener import *
from .database.database import *
from datetime import timedelta, datetime, timezone
import firebase_admin
from firebase_admin import credentials

# Get secrets info from config.ini
config_path = 'config.ini'
south_key = tools.read_config(config_path, 'NSHS', 'key')
south_secret = tools.read_config(config_path, 'NSHS', 'secret')
north_key = tools.read_config(config_path, 'NNHS', 'key')
north_secret = tools.read_config(config_path, 'NNHS', 'secret')

# Define API variables.
SCHOOLOGYCREDS = structs.SchoologyCreds(
    
    {
    structs.SchoolName.NEWTON_NORTH: north_key,
    structs.SchoolName.NEWTON_SOUTH: south_key, 
    }, 
    
    {
    structs.SchoolName.NEWTON_NORTH: north_secret,
    structs.SchoolName.NEWTON_SOUTH: south_secret
    }
    
    )

logger.add("logs/{time:YYYY-MM-DD}/absentListener.log", rotation="1 day", retention="7 days", format="{time} {level} {message}", filter="xxlimited", level="INFO")

# Listen for Schoology updates.
def listener():
    saturday = 5
    sunday = 6
    # debug mode
    debugMode = False

    holidays = []

    
    dailyCheckTimeStart = 7 # hour. Default: 7
    dailyCheckTimeEnd = 24 # hour. Default: 11
    
    resetTimeOne = (0, 0) # Midnight
    resetTimeTwo = (4, 20) # Light It Up

    schoologySuccessCheck = False
    dayoffLatch = False

    while True:
        currentTime = datetime.now(timezone.utc) - timedelta(hours=5) # Shift by 5 hours to get into EST.
        currentDate = currentTime.strftime('%d/%m/%Y')
        
        print(currentDate) 

        dayOfTheWeek = currentTime.weekday() 
        
        if not dayoffLatch:
            print("LISTENING", currentTime)

            print(f"Schoology Success: {schoologySuccessCheck}")
            
            if (dayOfTheWeek == saturday or dayOfTheWeek == sunday or currentDate in holidays) and not debugMode:
                if dayoffLatch == False:
                    logger.info(f"abSENT DAY OFF. LATCHING TO SLEEP! Day Number: {dayOfTheWeek}")
                    print(f"abSENT DAY OFF. LATCHING TO SLEEP! Day: {dayOfTheWeek}")
                    dayoffLatch = True
            else:
                aboveStartTime: bool = currentTime.hour >= dailyCheckTimeStart
                belowEndTime: bool = currentTime.hour <= dailyCheckTimeEnd
                if (aboveStartTime and belowEndTime and not schoologySuccessCheck) or debugMode: # IF its during the check time and schoology hasn't already been checked.
                    print("CHECKING SCHOOLOGY...")
                    sc = SchoologyListener(SCHOOLOGYCREDS)
                    schoologySuccessCheck: bool = sc.run()
                    print(f"Schoology Success: {schoologySuccessCheck}")
                    print("CHECK COMPLETE!")
                else:
                    if schoologySuccessCheck:
                        print("Not checking because schoology has alrady been checked.")
                    if not (aboveStartTime and belowEndTime):
                        print("Not checking because its not during the check time.")
            
        if (currentTime.hour == resetTimeOne[0] or currentTime.hour == resetTimeTwo[0]):
            # Reset schoologySuccessCheck to false @ midnight
            # Only change value when it is latched (true)
            logger.info("RESETTING all states to false")
            print("RESETTING STATE!", currentTime)
            dayoffLatch = False
            schoologySuccessCheck = False

        print("NOTIFY CALL TIMES: ", Notify.NUMBER_OF_CALLS)
        time.sleep(15) # Sleep for 15 seconds.

if __name__ == '__main__':
    # cred = credentials.Certificate("creds/firebase.json")
    # firebase = firebase_admin.initialize_app(cred)
    listener()