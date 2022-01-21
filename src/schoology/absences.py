from datetime import datetime
from dataTypes import structs, schemas, models
import schoolopy

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

        #print(absences)
        return absences

class ContentParser:
    def __init__(self, date):
        self.date = date
    
    def parse(self, update: structs.RawUpdate, school: structs.SchoolName):
        parsed = None

        if update == []:
            return None
        if school == structs.SchoolName.NEWTON_NORTH:
            update = self.deriveTable(update)
            update.columns = self.calculateColumns(update.content)
            map = self.mapNorth(update)
        else:
            update.columns = self.calculateColumns(update.content)
            map = self.mapSouth(update)
        
        rows = int(len(update.content)/update.columns)
        absences = []
        for row in range(rows):
            base = (row*update.columns)
            if update.content[base + map['NOTE']] == '':
                note = None
            else:
                note = update.content[base + map['NOTE']]
            # Define vars of important values.
            if 'FULLNAME' in map.keys():
                name = update.content[base + map['FULLNAME']].split(', ')
                first = name[1]
                last = name[0]
            else:
                first = update.content[base + map['FIRST']]
                last = update.content[base + map['LAST']]
            length = update.content[base + map['LENGTH']]
            
            teacher = schemas.TeacherCreate(first=first, last=last, school=school)
            object = schemas.AbsenceCreate(teacher=teacher, length=length, note=note)
            absences.append(object)
        
        for absence in absences:
            print(absence.teacher.first, absence.teacher.last, absence.length, absence.note)
        print("\n\n\n")

    def deriveTable(self, update: structs.RawUpdate):
        while update.content[0].lower() != ('position' or 'name'):
            update.content.pop(0)
        return update

    def mapNorth(self, update: structs.RawUpdate):
        map = {}
        for i in range(update.columns):
            if "position" in update.content[i].lower():
                map["POSITION"] = i
                continue
            if "first" in update.content[i].lower():
                map["FIRST"] = i
                continue
            if "last" in update.content[i].lower():
                map["LAST"] = i
                continue
            if "note" in update.content[i].lower():
                map["NOTE"] = i
                continue
            if "day" in update.content[i].lower():
                map["LENGTH"] = i
                continue
            if "name" in update.content[i].lower():
                map["FULLNAME"] = i
                continue
        return map

    def mapSouth(self, update: structs.RawUpdate):
        map = {}

        weekdays = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")

        for i in range(update.columns):
            for weekday in weekdays:
                if weekday.lower() in update.content[i].lower():
                    map["DOW"] = i
        for i in range(update.columns):
            if "day" in update.content[i].lower() and i not in map.values():
                map["LENGTH"] = i
        for i in range(update.columns):
            if self.date.strftime("%-m/%-d/%Y") in update.content[i].lower() and i not in map.values():
                map["DATE"] = i
        map["FIRST"] = 1
        map["LAST"] = 0   
        for i in range(update.columns):
            if i not in map.values() and "NOTE" not in map.keys():
                map["NOTE"] = i
        return map

    def calculateColumns(self, table: list):
        lineBreaks = [i for i, x in enumerate(table) if x == ""] # Generates list of linebreaks and their indexes.
        for i, lineBreak in enumerate(lineBreaks):
            if lineBreak + 1 == lineBreaks[i+1]:
                columns = lineBreak/(i+1)
                if lineBreaks[i+1] + 1 == lineBreaks[i+2]:
                    columns = (lineBreak + 1)/(i+1)
                break;
        return int(columns+2)

    # def susanSpirito(self, rawTable: list):
    #     # Absence list.
    #     absences = []

    #     # Pop until correct position.
    #     while rawTable[0] != "Position":
    #         rawTable.pop(0)

    #     # Set number of COLUMNS
    #     COLUMNS = self.calculateColumns(rawTable)
    #     for _ in range(COLUMNS):
    #         rawTable.pop(0)

    #     # Calculate number of rows.
    #     rows = int(len(rawTable)/COLUMNS)

    #     # Generate correct object for row in table.
    #     for row in range(rows):
    #         # Set the note correctly.
    #         if rawTable[row*COLUMNS+5] == '':
    #             note = None
    #         else:
    #             note = rawTable[row*COLUMNS+5]
    #         # Generate AbsentTeacher for row.
    #         teacher = schemas.AbsenceCreate(teacher=schemas.TeacherCreate(first=rawTable[row*COLUMNS+2], last=rawTable[row*COLUMNS+1], school=structs.SchoolName.NEWTON_NORTH), length=rawTable[row*COLUMNS+3], note=note)
    #         absences.append(teacher)

    #     return absences

    # def caseyFriend(self, rawTable: list):
    #     # Set absences.
    #     absences = []

    #     while rawTable[0] != 'Name' and rawTable[0] != 'Position':
    #         rawTable.pop(0)

    #     COLUMNS = self.calculateColumns(rawTable)

    #     # Clause #1 - Compact, when name is first column.
    #     if rawTable[0] == 'Name':
    #         # Pop label row.
    #         for _ in range(COLUMNS):
    #             rawTable.pop(0)
    #         # Set number of rows.
    #         rows = int(len(rawTable)/COLUMNS)

    #         for row in range(rows):
    #             # Set note correctly.
    #             if rawTable[row*COLUMNS+1] == '':
    #                 note = None
    #             else:
    #                 note = rawTable[row*COLUMNS+1]
    #             # Split the name.
    #             name = rawTable[row*COLUMNS].split(", ")
    #             # Generate AbsentTeacher object for row.
    #             teacher = schemas.AbsenceCreate(teacher=schemas.TeacherCreate(first=name[1], last=name[0], school=structs.SchoolName.NEWTON_NORTH), length=rawTable[row*COLUMNS+3], note=note)
    #             absences.append(teacher)

    #     # Clause #2 - Standard, with position as first column, 8 columns, and DoW as last.
    #     elif rawTable[0] == 'Position' and rawTable[5] == 'DoW':
    #         # Pop label row.
    #         for _ in range(COLUMNS):
    #             rawTable.pop(0)
    #         # Set number of rows.
    #         rows = int(len(rawTable)/COLUMNS)
    #         for row in range(rows):
    #             # Set note correctly.
    #             if rawTable[row*COLUMNS+3] == '':
    #                 note = None
    #             else:
    #                 note = rawTable[row*COLUMNS+3]
    #             # Generate AbsentTeacher object for row.
    #             teacher = schemas.AbsenceCreate(teacher=schemas.TeacherCreate(first=rawTable[row*COLUMNS+2], last=rawTable[row*COLUMNS+1], school=structs.SchoolName.NEWTON_NORTH), length=rawTable[row*COLUMNS+4], note=note)
    #             absences.append(teacher)
        
    #     # Clause #3 - Short, same as #2 without DoW.
    #     elif rawTable[0] == 'Position' and rawTable[4] == 'Day':
    #         # Pop label row.
    #         for _ in range(COLUMNS):
    #             rawTable.pop(0)
    #         # Set number of rows.
    #         rows = int(len(rawTable)/COLUMNS)
    #         for row in range(rows):
    #             # Set the note correctly.
    #             if rawTable[row*COLUMNS+3] == '':
    #                 note = None
    #             else:
    #                 note = rawTable[row*COLUMNS+3]
    #             # Generate AbsentTeacher object for row.
    #             teacher = schemas.AbsenceCreate(teacher=schemas.TeacherCreate(first=rawTable[row*COLUMNS+2], last=rawTable[row*COLUMNS+1], school=structs.SchoolName.NEWTON_NORTH), length=rawTable[row*COLUMNS+4], note=note)
    #             absences.append(teacher)

    #     return absences

    # def tracyConnolly(self, rawTable: list):
    #     # Set number of columns.
    #     COLUMNS = self.calculateColumns(rawTable)
    #     # Absence list.
    #     absences = []
    #     # Calculate number of rows.
    #     rows = int(len(rawTable)/COLUMNS)

    #     for row in range(rows):
    #         # Set the note correctly.
    #         if rawTable[row*COLUMNS+4] == '':
    #             note = None
    #         else:
    #             note = rawTable[row*COLUMNS+4]
    #         # Generate AbsentTeacher for row.
    #         teacher = schemas.AbsenceCreate(teacher=schemas.TeacherCreate(first=rawTable[row*COLUMNS+1], last=rawTable[row*COLUMNS], school=structs.SchoolName.NEWTON_SOUTH), length=rawTable[row*COLUMNS+2], note=note)
    #         absences.append(teacher)

    #     return absences


                