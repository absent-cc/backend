from datetime import datetime, timedelta, timezone
import yaml
from dataTypes import structs
from notifications.firebase import *
from .absences import Absences
from configparser import ConfigParser
class SchoologyListener:
    def __init__(self, SCHOOLOGYCREDS):
        self.north = structs.SchoolName.NEWTON_NORTH
        self.south = structs.SchoolName.NEWTON_SOUTH
        self.restTime = timedelta(seconds=10)
        self.sc = Absences(SCHOOLOGYCREDS)

    # Run function, for listening and calling notifications code.
    def run(self) -> bool:
        date = datetime.now(timezone.utc) - timedelta(hours=5) # Convert from UTC --> EST

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
            
            # Add the absences to the database.
            for absence in absences:
                # Check if the absence is already in the database.
                if not self.sc.addAbsence(absence): # If action was unsuccessful, then the absence is already in the database.
                    print("Absence already in database.")
                    statuses[self.south].absences = True # Update status that action was committed previously.
                    break
                
            if not statuses[self.south].notifications:
                print("ADD IN NOTIFY CODE HERE LATER")

        def northRun() -> bool:
            # Get the absences
            absences = self.sc.filterAbsencesNorth(date)

            # Add the absences to the database.
            for absence in absences:
                # Check if the absence is already in the database.
                if not self.sc.addAbsence(absence): # If action was unsuccessful, then the absence is already in the database.
                    print("Absence already in database.")
                    statuses[self.north].absences = True # Update status that action was committed previously.
                    break
                
            if not statuses[self.north].notifications:
                print("ADD IN NOTIFY CODE HERE LATER")
        
        return southRun() and northRun()

    # Function for fetching an up to date state file content.
    def fetchStates(self, date, statePath: str= 'state.ini'):
        stateDict = {
            structs.SchoolName.NEWTON_NORTH: False,
            structs.SchoolName.NEWTON_SOUTH: False
        }
        # Read state yaml file.

        state = ConfigParser()
        state.read(statePath)
        if state[f"{structs.SchoolName.NEWTON_NORTH}"]['updated'] == date.strftime('%m/%-d/%Y'):
            stateDict[structs.SchoolName.NEWTON_NORTH] = True
        if state[f"{structs.SchoolName.NEWTON_SOUTH}"]['updated'] == date.strftime('%m/%-d/%Y'):
            stateDict[structs.SchoolName.NEWTON_SOUTH] = True
        return stateDict

    # Function for writing state.
    def writeState(self, school: structs.SchoolName, date, statePath = 'state.ini'):
        state = ConfigParser()
        state.read(statePath)
        # Read state ini file.            
        state[str(school)] = date.strftime('%m/%-d/%Y')
        if school == structs.SchoolName.NEWTON_NORTH:
            state[str(structs.SchoolName.NEWTON_SOUTH)] = state[str(structs.SchoolName.NEWTON_SOUTH)]
        else:
            state[str(structs.SchoolName.NEWTON_NORTH)] = state[str(structs.SchoolName.NEWTON_NORTH)]
        # Write new state to state file
        with open('state.yml', 'w') as f:
            yaml.safe_dump(state, f)
        return state