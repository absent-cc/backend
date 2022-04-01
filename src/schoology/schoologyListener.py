from datetime import datetime, timedelta, timezone

from src.dataTypes import models
from src.dataTypes.schemas import TeacherReturn

from ..dataTypes import structs
from ..notifications.notify import Notify
from .absences import AbsencePuller
from configparser import ConfigParser
from ..database.database import SessionLocal
from ..database import crud

from loguru import logger


logger.add("logs/{time:YYYY-MM-DD}/schoologyListener.log", rotation="1 day", retention="7 days", format="{time} {level} {message}", filter="xxlimited", level="INFO")

class SchoologyListener:
    def __init__(self, SCHOOLOGYCREDS):
        self.north = structs.SchoolName.NEWTON_NORTH
        self.south = structs.SchoolName.NEWTON_SOUTH
        self.restTime = timedelta(seconds=30)
        self.sc = AbsencePuller(SCHOOLOGYCREDS)
        self.db = SessionLocal()

    # Run function, for listening and calling notifications code.
    def run(self) -> bool:
        date = datetime.now(timezone.utc) - timedelta(hours=5) # Convert from UTC --> EST

        # These statuses get updated when the listern is run.
        ## What happens is that each run function sees if the absent teachers have already been added to the database.
        ## They then update the statuses to reflect that, so in essence the state is now stored as a computed property of the absences table in the database.
        statuses = {
            # School : Tuple(pull status, notify status)
            structs.SchoolName.NEWTON_SOUTH: structs.ListenerStatus(school = self.south), # Default is False, False (Always pull, always notify)
            structs.SchoolName.NEWTON_NORTH: structs.ListenerStatus(school = self.north)
        }

        def southRun() -> bool:
            # Get the absences
            absences = self.sc.filterAbsencesSouth(date)

            if absences == None:
                return False
             
            # Add the absences to the database.
            for absence in absences:
                # Check if the absence is already in the database.
                self.sc.addAbsence(absence)
                # if not self.sc.addAbsence(absence): # If action was unsuccessful, then the absence is already in the database.
                #print("SOUTH: Absence already in database.")
                    # statuses[self.south].absences = True # Update status that action was committed previously.
                    # statuses[self.south].notifications = True # Update status was probably action was committed previously.
                    # break
            #statuses[self.south].absences = True # Update status that action was committed previously.
            
            southAbsences = crud.getAbsenceList(self.db, school=structs.SchoolName.NEWTON_SOUTH)
            southAbsencesExist = len(southAbsences) != 0

            if southAbsencesExist:
                print("HERE")
                statuses[self.south].updateState(True, None)

            if (not statuses[self.south].notifications) and southAbsencesExist:
                logger.info("SHOULD BE SENDING NOTIFICATIONS: SOUTH")
                print("SHOULD BE SENDING NOTIFS SOUTH")
                Notify(structs.SchoolName.NEWTON_SOUTH).sendMessages()
                statuses[self.south].updateState(True, True)
                return True
                
            return (statuses[self.south].notifications and statuses[self.south].absences)

        def northRun() -> bool:
            # Get the absences
            absences = self.sc.filterAbsencesNorth(date)

            if absences == None:
                return False

            # Add the absences to the database.
            for absence in absences:
                # Check if the absence is already in the database.
                self.sc.addAbsence(absence) # If action was unsuccessful, then the absence is already in the database.
                # if not self.sc.addAbsence(absence): # If action was unsuccessful, then the absence is already in the database.
                    # statuses[self.south].absences = True # Update status that action was committed previously.
                    # statuses[self.south].notifications = True # Update status was probably action was committed previously.
                    # break

            northAbsences = crud.getAbsenceList(self.db, school=structs.SchoolName.NEWTON_NORTH)
            northAbsencesExist = len(northAbsences) != 0

            if northAbsencesExist:
                statuses[self.north].updateState(True, None)
            
            if (not statuses[self.north].notifications) and northAbsencesExist:
                logger.info("SHOULD BE SENDING NOTIFICATIONS: NORTH")
                print("SHOULD BE SENDING NOTIFICATIONS NORTH")
                Notify(structs.SchoolName.NEWTON_NORTH).sendMessages()
                statuses[self.north].notifications = True
                statuses[self.north].updateState(True, True)
                return True

            return (statuses[self.north].notifications and statuses[self.north].absences)
        
        southRes = southRun()
        northRes = northRun()

        if southRes == None or northRes == None:
            print("South res or North Res is None. That is WRONG!")

        print(f"South Res: {southRes}, North Res: {northRes}")
        return southRes and northRes

# if __name__ == "__main__":
#     config = ConfigParser()
#     config.read('config.ini')
#     creds = config['SCHOOLOGY']
#     sl = SchoologyListener(creds)
#     sl.run()
