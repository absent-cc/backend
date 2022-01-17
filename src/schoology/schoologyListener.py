from datetime import datetime, timedelta, timezone
import yaml
from dataStructs import *
from notifications.firebase import *
from database.logger import Logger

class SchoologyListener:
    def __init__(self, SCHOOLOGYCREDS, ):
        self.north = SchoolName.NEWTON_NORTH
        self.south = SchoolName.NEWTON_SOUTH
        self.restTime = timedelta(seconds=10)
        
        # Logging:
        self.logger = Logger()

    # Run function, for listening and calling notifications code.
    def run(self) -> bool:

        date = datetime.now(timezone.utc) - timedelta(hours=5) # Convert from UTC --> EST
        # Reads from state file to determine whether notifications have been sent today.
        states = self.fetchStates(date)
        
        # NNHS Runtime.
        if states[self.north] == False:
            update = self.notifications.run(date, self.north) # Sends notifications, checks sucess.
            if update:
                self.writeState(self.north, date) # Update statefile and var.
                self.logger.sentAbsencesSuccess(SchoolName.NEWTON_NORTH)

        # NSHS Runtime
        if states[self.south] == False:
            update = self.notifications.run(date, self.south) # Sends notifications, check sucess.
            if update:
                self.writeState(self.south, date) # Update statefile and var.
                self.logger.sentAbsencesSuccess(SchoolName.NEWTON_SOUTH)
        
        states = self.fetchStates(date)
        
        return states[self.north] and states[self.south]

    # Function for fetching an up to date state file content.
    def fetchStates(self, date, statePath = 'state.yml'):
        stateDict = {
            SchoolName.NEWTON_NORTH: False,
            SchoolName.NEWTON_SOUTH: False
        }
        # Read state yaml file.
        with open(statePath, 'r') as f:
            state = yaml.safe_load(f)
        if state[str(SchoolName.NEWTON_NORTH)] == date.strftime('%m/%-d/%Y'):
            stateDict[SchoolName.NEWTON_NORTH] = True
        if state[str(SchoolName.NEWTON_SOUTH)] == date.strftime('%m/%-d/%Y'):
            stateDict[SchoolName.NEWTON_SOUTH] = True
        return stateDict

    # Function for writing state.
    def writeState(self, school: SchoolName, date, statePath = 'state.yml'):
        # Read state yaml file.
        with open(statePath, 'r') as f:
            state = yaml.safe_load(f)
        state[str(school)] = date.strftime('%m/%-d/%Y')
        if school == SchoolName.NEWTON_NORTH:
            state[str(SchoolName.NEWTON_SOUTH)] = state[str(SchoolName.NEWTON_SOUTH)]
        else:
            state[str(SchoolName.NEWTON_NORTH)] = state[str(SchoolName.NEWTON_NORTH)]
        # Write new state to state file
        with open('state.yml', 'w') as f:
            yaml.safe_dump(state, f)
        return state