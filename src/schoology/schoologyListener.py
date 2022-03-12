from datetime import datetime, timedelta, timezone

from ..dataTypes import structs
from ..notifications import firebase
from .absences import AbsencePuller
from configparser import ConfigParser
class SchoologyListener:
    def __init__(self, SCHOOLOGYCREDS):
        self.north = structs.SchoolName.NEWTON_NORTH
        self.south = structs.SchoolName.NEWTON_SOUTH
        self.restTime = timedelta(seconds=30)
        self.sc = AbsencePuller(SCHOOLOGYCREDS)

    # Run function, for listening and calling notifications code.
    def run(self) -> bool:
        date = datetime.now(timezone.utc) - timedelta(hours=30) # Convert from UTC --> EST

        # These statuses get updated when the listern is run.
        ## What happens is that each run function sees if the absent teachers have already been added to the database.
        ## They then update the statuses to reflect that, so in essence the state is now stored as a computed property of the absences table in the database.
        statuses = {
            # School : Tuple(pull status, notify status)
            structs.SchoolName.NEWTON_SOUTH: structs.ListenerStatus(), # Default is False, False (Always pull, always notify)
            structs.SchoolName.NEWTON_NORTH: structs.ListenerStatus()
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
                #if not self.sc.addAbsence(absence): # If action was unsuccessful, then the absence is already in the database.
                #print("SOUTH: Absence already in database.")
                #     statuses[self.south].absences = True # Update status that action was committed previously.
                #     break
            #statuses[self.south].absences = True # Update status that action was committed previously.
                
            if not statuses[self.south].notifications:
                print("SOUTH: ADD IN NOTIFY CODE HERE LATER")
                return True

        def northRun() -> bool:
            # Get the absences
            absences = self.sc.filterAbsencesNorth(date)

            if absences == None:
                return False

            # Add the absences to the database.
            for absence in absences:
                # Check if the absence is already in the database.
                self.sc.addAbsence(absence) # If action was unsuccessful, then the absence is already in the database.
                #    print("NORTH: Absence already in database.")
                #    statuses[self.north].absences = True # Update status that action was committed previously.
                #    break
                
            if not statuses[self.north].notifications:
                print("NORTH: ADD IN NOTIFY CODE HERE LATER")
                return True
        
        southRes = southRun()
        northRes = northRun()
        return southRes and northRes

if __name__ == "__main__":
    config = ConfigParser()
    config.read('config.ini')
    creds = config['SCHOOLOGY']
    sl = SchoologyListener(creds)
    sl.run()