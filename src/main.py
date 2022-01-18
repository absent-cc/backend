import threading, time, yaml
from dataStructs import *
from schoology.schoologyListener import *
from database.database import *
from datetime import timedelta, datetime, timezone

# Open files.
with open('secrets.yml') as f:
    cfg = yaml.safe_load(f)

# Define API variables.
SCHOOLOGYCREDS = SchoologyCreds(
    
    {
    SchoolName.NEWTON_NORTH: cfg['north']['key'],
    SchoolName.NEWTON_SOUTH: cfg['south']['key'] 
    }, 
    
    {
    SchoolName.NEWTON_NORTH: cfg['north']['secret'],
    SchoolName.NEWTON_SOUTH: cfg['south']['secret']
    }
    
    )

# Make threads regenerate on fault.
def threadwrapper(func):
    def wrapper():
        while True:
            try:
                func()
            except BaseException as error:
                print('abSENT - {!r}; restarting thread'.format(error))
            else:
                print('abSENT - Exited normally, bad thread, restarting')
    return wrapper

# Listen for Schoology updates.
def sc_listener():
    saturday = 5
    sunday = 6
    holidays = []

    # debug mode
    debugMode = False

    dailyCheckTimeStart = 7 # hour
    dailyCheckTimeEnd = 12 # hour
    
    resetTime = (0, 0) # midnight

    schoologySuccessCheck = False
    dayoffLatch = False
    while True:
        currentTime = datetime.now(timezone.utc) - timedelta(hours=5) # Shift by 5 hours to get into EST.
        currentDate = currentTime.strftime('%d/%m/%Y')
        dayOfTheWeek = currentTime.weekday() 
        
        print("LISTENING", currentTime)

        if (dayOfTheWeek == saturday or dayOfTheWeek == sunday or currentDate in holidays) and not debugMode:
            if dayoffLatch == False:
                logger.schoologyOffDay(currentDate)
                print("abSENT DAY OFF")
                dayoffLatch = True
        else:
            aboveStartTime: bool = currentTime.hour >= dailyCheckTimeStart
            belowEndTime: bool = currentTime.hour <= dailyCheckTimeEnd
            if (aboveStartTime and belowEndTime and not schoologySuccessCheck) or debugMode:
                print("CHECKING SCHOOLOGY.")
                sc = SchoologyListener(textnowCreds, SCHOOLOGYCREDS)
                schoologySuccessCheck = sc.run()
                print("CHECK COMPLETE.")
        
        if currentTime.hour == resetTime[0] and currentTime.minute == resetTime[1]:
            # Reset schoologySuccessCheck to false @ midnight
            # Only change value when it is latched (true)
            if schoologySuccessCheck == True:
                print("RESTART")
                logger.resetSchoologySuccessCheck()
                dayoffLatch = False
                schoologySuccessCheck = False

        time.sleep(15) # Sleep for 15 seconds.
            
# Configure and start threads.
threads = {
        'sc': threading.Thread(target=threadwrapper(sc_listener), name='sc listener'),
}

threads['sc'].start()