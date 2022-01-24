from datetime import datetime
from dataTypes import structs, schemas, models
import schoolopy
import statistics
from .parsing.columnDetection import ColumnDetection

class Absences:
    # Sets up the two API objects as entries within a list 'api' . 
    def __init__(self, scCreds: structs.SchoologyCreds):
        northkey = scCreds.keys[structs.SchoolName.NEWTON_NORTH]
        northsecret = scCreds.secrets[structs.SchoolName.NEWTON_NORTH]
        southkey = scCreds.keys[structs.SchoolName.NEWTON_SOUTH]
        southsecret = scCreds.secrets[structs.SchoolName.NEWTON_SOUTH]
        self.api = {
            structs.SchoolName.NEWTON_NORTH: schoolopy.Schoology(schoolopy.Auth(northkey, northsecret)),
            structs.SchoolName.NEWTON_SOUTH: schoolopy.Schoology(schoolopy.Auth(southkey, southsecret))
        }
        self.api[structs.SchoolName.NEWTON_NORTH].limit = 10
        self.api[structs.SchoolName.NEWTON_SOUTH].limit = 10

    # Gets the feed, accepting an argument 'school' which is either 0 or 1, 0 corresponding to North and 1 corresponding to South (this value being the same as the school's index within the API array). Grabs all updates posted by individuals of interest and saves them to an array 'feed', and returns that array.
    def getFeed(self, school: structs.SchoolName):
        teachers = ["Tracy Connolly", "Casey Friend", "Suzanne Spirito"]
        feed = []
        for update in self.api[school].get_feed():
            user = self.api[school].get_user(update.uid)
            if user.name_display in teachers:
                feed.append((user.name_display, update.body, update.last_updated))
        return feed

    # Gets the absence table for the date requested as defined by 'date'. Returns just this update for furthing processing. The date argument ultimately comes from the call of this function in main.py.
    def getCurrentTable(self, school: structs.SchoolName):
        feed = self.getFeed(school)
        for update in feed:
            postDate = datetime.utcfromtimestamp(int(update[2]))
            if self.date.date() == postDate.date():
                return structs.RawUpdate(content=update[1].split("\n"), poster=update[0])
        return None

    # Takes the raw North attendance table from the prior function and parses it, using the AbsentTeacher dataclass. Returns an array of entries utilizing this class. 
    def filterAbsencesNorth(self, date):       
        self.date = date
        table = self.getCurrentTable(structs.SchoolName.NEWTON_NORTH)  
        absences = ContentParser(date).parse(table, structs.SchoolName.NEWTON_NORTH)

        return absences

    # Same as the above, but the parsing is handled slightly differently due to the South absence table being differenct in formatting.
    def filterAbsencesSouth(self, date):
        self.date = date
        table = self.getCurrentTable(structs.SchoolName.NEWTON_SOUTH)    
        absences = ContentParser(date).parse(table, structs.SchoolName.NEWTON_SOUTH)

        return absences

class ContentParser:
    def __init__(self, date):
        self.date = date
    
    def parse(self, update: structs.RawUpdate, school: structs.SchoolName):
        parsed = None

        if update == []:
            return None
        if school == structs.SchoolName.NEWTON_NORTH:
            # col = ColumnDetection(structs.SchoolName.NEWTON_NORTH)
            # update = self.deriveTable(update)
            # cols = self.calculateColumns(update.content)
            # update.columns = cols[0]
            # update.content = [update.content[i:i+update.columns] for i in range(0,len(update.content),update.columns)]
            # col.titleDetector(update)
            # #map = self.mapNorth(update)
            pass
        else:
            col = ColumnDetection(structs.SchoolName.NEWTON_SOUTH)
            cols = self.calculateColumns(update.content)
            print(cols)
            update.columns = cols[0]
            update.content = [update.content[i:i+update.columns] for i in range(0,len(update.content),update.columns)]
            col.titleDetector(update)
        
        # rows = int(len(update.content)/update.columns)
        # absences = []
        # for row in range(rows):
        #     base = (row*update.columns)
        #     if update.content[base + map['NOTE']] == '':
        #         note = None
        #     else:
        #         note = update.content[base + map['NOTE']]
        #     # Define vars of important values.
        #     if 'FULLNAME' in map.keys():
        #         name = update.content[base + map['FULLNAME']].split(', ')
        #         first = name[1]
        #         last = name[0]
        #     else:
        #         first = update.content[base + map['FIRST']]
        #         last = update.content[base + map['LAST']]
        #     length = update.content[base + map['LENGTH']]
            
        #     teacher = schemas.TeacherCreate(first=first, last=last, school=school)
        #     object = schemas.AbsenceCreate(teacher=teacher, length=length, note=note)
        #     absences.append(object)
        
        # for absence in absences:
        #     print(absence.teacher.first, absence.teacher.last, absence.length, absence.note)
        # print("\n\n\n")

    def deriveTable(self, update: structs.RawUpdate):
        while update.content[0].lower() != ('position' or 'name'):
            update.content.pop(0)
        return update

    def calculateColumns(self, table: list):
        lineBreaks = [i for i, x in enumerate(table) if x == ""] # Generates list of linebreaks and their indexes.
        possibleColumns = []
        index = 1 # Counter for rows counted.
        for i, lineBreak in enumerate(lineBreaks): # Iterates through a list of linebreaks and their indexes.
            try:
                if lineBreak + 1 == lineBreaks[i+1]: # Checks for double space.
                    if lineBreaks[i+1] + 1 == lineBreaks[i+2]: # Checks if this is a triple set of spaces. 
                        continue # If it is, ignore it.
                    possibleColumns.append(int((lineBreak + 2) / index)) # Appends this rows column calculation.
                    index += 1 # Tracks # of rows counted.
            except IndexError:
                break
        mode = statistics.mode(possibleColumns) # Gets most common value of column count.
        confidence = possibleColumns.count(mode) / len(possibleColumns) # Gets confidence.
        return mode, confidence
