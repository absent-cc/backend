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
        # Reads from state file to determine whether notifications have been sent today.
        states = self.fetchStates(date)
        
        # NNHS Runtime.
        if states[self.north] == False:
            self.sc.filterAbsencesNorth(date)
            #update = self.notifications.run(date, self.north) # Sends notifications, checks sucess.
            #if update:
            #    self.writeState(self.north, date) # Update statefile and var.

        # NSHS Runtime
        if states[self.south] == False:
            self.sc.filterAbsencesSouth(date)
            #update = self.notifications.run(date, self.south) # Sends notifications, check sucess.
            
            #if update:
            #    self.writeState(self.south, date) # Update statefile and var.
        
        states = self.fetchStates(date)
        
        return states[self.north] and states[self.south]

    # Function for fetching an up to date state file content.
    def fetchStates(self, date, statePath = 'state.ini'):
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
    def writeState(self, school: structs.SchoolName, date, statePath = 'state.yml'):
        # Read state yaml file.
        with open(statePath, 'r') as f:
            state = yaml.safe_load(f)
        state[str(school)] = date.strftime('%m/%-d/%Y')
        if school == structs.SchoolName.NEWTON_NORTH:
            state[str(structs.SchoolName.NEWTON_SOUTH)] = state[str(structs.SchoolName.NEWTON_SOUTH)]
        else:
            state[str(structs.SchoolName.NEWTON_NORTH)] = state[str(structs.SchoolName.NEWTON_NORTH)]
        # Write new state to state file
        with open('state.yml', 'w') as f:
            yaml.safe_dump(state, f)
        return state