from datetime import datetime, timedelta, timezone
from ...dataTypes import structs, tools
from ...schoology.absences import Absences
from typing import List, Optional

relative_path = "src/tools/schoology"

class VariableSchoologyListener:
    def __init__(self, SCHOOLOGYCREDS):
        self.north = structs.SchoolName.NEWTON_NORTH
        self.south = structs.SchoolName.NEWTON_SOUTH
        self.restTime = timedelta(seconds=10)
        self.sc = Absences(SCHOOLOGYCREDS)

    def pullRaw(self, date: datetime) -> dict[structs.SchoolName, list[str]]:
        # Get the raw absences message
        raw = {}
        for school in structs.SchoolName:
            table = self.sc.getCurrentTable(school.value, date)
            raw[school] = table
        
        print(raw)
        return raw

    # Run function, for listening and calling notifications code.
    def pullFiltered(self, date: datetime) -> dict[structs.SchoolName, list[str]]:

        def southPull() -> Optional[list]:
            # Get the absences
            absences = self.sc.filterAbsencesSouth(date)

            if absences == None:
                return None
            
            return absences
        
        def northPull() -> Optional[list]:
            # Get the absences
            absences = self.sc.filterAbsencesNorth(date)

            if absences == None:
                return None
            
            return absences
        
        return {
            structs.SchoolName.NEWTON_SOUTH: southPull(), 
            structs.SchoolName.NEWTON_NORTH: northPull()
            }

    def writeRawToFile(self, raw: dict[structs.SchoolName, list[str]], date: datetime, rawFileBasePath: str = f"{relative_path}/data/rawFeed"):
        print("RAW", raw)
        for school, feed in raw.items():
            with open(f"{rawFileBasePath}/raw_{school.value}.txt", "w+") as f:
                f.write(f"--- {date} ---\n")
                strToWrite = ""
                for line in feed.content:
                    print("Line", line)
                    strToWrite += line + "\n"
                strToWrite = strToWrite[:-2]
                f.write(strToWrite + "\n")
                print("STR TO WRITE", strToWrite)

    def run(self, dates: List[datetime]):
        for date in dates:
            raw = self.pullRaw(date)
            if raw[structs.SchoolName.NEWTON_NORTH] == None or raw[structs.SchoolName.NEWTON_SOUTH] == None:
                print("No absences to add.")
                continue
            self.writeRawToFile(raw, date)

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

if __name__ == "__main__":
    listener = VariableSchoologyListener(SCHOOLOGYCREDS)
    listener.run([datetime.now(timezone.utc) - timedelta(days=2), datetime.now(timezone.utc)])

