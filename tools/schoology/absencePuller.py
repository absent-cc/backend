from datetime import datetime, timedelta, timezone

from pytest import Session

from .helper.dateRangeGen import dateRangeGen

# Uses the compiled src package rather than the code itself!
from src.dataTypes import structs, tools
from src.schoology.absences import Absences
from typing import List, Optional
from src.api import accounts

relative_path = "src/tools/schoology"

class VariableSchoologyWriter:
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
    
    def updateDatabase(self, filteredAbsences: dict[structs.SchoolName, list[str]], date: datetime, db: Session = accounts.getDBSession):
        for school, absences in filteredAbsences.items():
            if absences == None:
                print(f"{date}: No absences for {school}")
                continue
            for absence in absences:
                if not self.sc.addAbsence(absence):
                    print(f"Absences already exist for {date}. Probs some error in your code.")
                    continue
            print(f"{date}: Added {len(absences)} absences for {school}")

        print()
    
    def writeRawToFile(self, raw: dict[structs.SchoolName, list[str]], date: datetime, rawFileBasePath: str = f"{relative_path}/data/rawFeed"):
        for school, feed in raw.items():
            if feed == None:
                print(f"{date}: No absences for {school}")
                continue
            with open(f"{rawFileBasePath}/raw_{school.value}.txt", "a+") as f:
                f.write(f"--- {date} ---\n")
                strToWrite = ""
                for line in feed.content:
                    strToWrite += line + "\n"
                strToWrite = strToWrite[:-2]
                f.write(strToWrite + "\n")
            print(f"{date}: Wrote raw feed to file for {school}")
        print()

    def run(self, dates: List[datetime]):
        print("--- UPDATING DATABASE ---")
        for date in dates:
            absences = self.pullFiltered(date)
            self.updateDatabase(absences, date)

        # print("--- RAW FEED TO TXT ---")
        # for date in dates:
        #     self.writeRawToFile(self.pullRaw(date), date)
            # raw = self.pullRaw(date)
            # if raw[structs.SchoolName.NEWTON_NORTH] == None or raw[structs.SchoolName.NEWTON_SOUTH] == None:
            #     print("No absences to add.")
            #     continue
            # self.writeRawToFile(raw, date)

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
    writer = VariableSchoologyWriter(SCHOOLOGYCREDS)
    dates = dateRangeGen(datetime(2022, 2, 10), datetime(2022, 2, 20))
    writer.run(dates)