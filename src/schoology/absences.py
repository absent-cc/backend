from dataStructs import *
import schoolopy

class Absences:
    # Sets up the two API objects as entries within a list 'api' . 
    def __init__(self, scCreds: SchoologyCreds):
        self.api = {
            SchoolName.NEWTON_NORTH: schoolopy.Schoology(schoolopy.Auth(scCreds.northkey, scCreds.northsecret)),
            SchoolName.NEWTON_SOUTH: schoolopy.Schoology(schoolopy.Auth(scCreds.southkey, scCreds.southsecret))
        }
        self.api[SchoolName.NEWTON_NORTH].limit = 10
        self.api[SchoolName.NEWTON_SOUTH].limit = 10

    # Gets the feed, accepting an argument 'school' which is either 0 or 1, 0 corresponding to North and 1 corresponding to South (this value being the same as the school's index within the API array). Grabs all updates posted by individuals of interest and saves them to an array 'feed', and returns that array.
    def getFeed(self, school: SchoolName):
        teachers = ["Tracy Connolly","Casey Friend","Suzanne Spirito"]
        feed = []
        for update in self.api[school].get_feed():
            user = self.api[school].get_user(update.uid)
            if user.name_display in teachers:
                feed.append((user.name_display, update.body))
        return feed

    # Gets the absence table for the date requested as defined by 'date'. Returns just this update for furthing processing. The date argument ultimately comes from the call of this function in main.py.
    def getAbsenceTable(self, school: SchoolName):
        validDates = [
            # Tracy Connolly
            self.date.strftime("%m/%-d/%Y"),
            self.date.strftime("%-m/%-d/%Y"),
            # Susan Spiritio
            self.date.strftime('%m/%-d/%y'),
            # Casey Friend
            self.date.strftime('%b. %-d'),
            self.date.strftime('%B %-d'),
        ]

        feed = self.getFeed(school)
        current_table = None
        for update in feed:
            text = update[1].split("\n")
            # Table has historically had date on 4th column, used to differentiate between update and actual attendance table
            if len(text) > 4:
                for date in validDates:
                    if date in text[3]:
                        current_table = (update[0], text)
                    elif date in text[0]:
                        current_table = (update[0], text)
                    elif date in text[8]:
                        current_table = (update[0], text)
            
        return current_table

    # Takes the raw North attendance table from the prior function and parses it, using the AbsentTeacher dataclass. Returns an array of entries utilizing this class. 
    def filterAbsencesNorth(self, date):       
        self.date = date
        table = self.getAbsenceTable(SchoolName.NEWTON_NORTH)    
        absences = ContentParser(date).parse(table)

        print(absences)
        return absences

    # Same as the above, but the parsing is handled slightly differently due to the South absence table being differenct in formatting.
    def filterAbsencesSouth(self, date):
        self.date = date
        table = self.getAbsenceTable(SchoolName.NEWTON_SOUTH)    
        absences = ContentParser(date).parse(table)

        print(absences)
        return absences

class ContentParser:
    def __init__(self, date):
        self.date = date
    
    def parse(self, rawTable: list):
        parsed = None
        if rawTable == None:
            return None
        elif rawTable[0] == 'Casey Friend':
            parsed = self.caseyFriend(rawTable[1])
        elif rawTable[0] == 'Susan Spirito':
            parsed = self.susanSpirito(rawTable[1])
        elif rawTable[0] == 'Tracy Connolly':
            parsed = self.tracyConnolly(rawTable[1])
        return parsed

    def susanSpirito(self, rawTable: list):
        # Absence list.
        absences = []

        # Pop until correct position.
        while rawTable[0] != "Position":
            rawTable.pop(0)
        # Set number of COLUMNS
        COLUMNS = 8
        for _ in range(COLUMNS):
            rawTable.pop(0)

        # Calculate number of rows.
        rows = int(len(rawTable)/COLUMNS)

        # Generate correct object for row in table.
        for row in range(rows):
            # Set the note correctly.
            if rawTable[row*COLUMNS+5] == '':
                note = None
            else:
                note = rawTable[row*COLUMNS+5]
            # Generate AbsentTeacher for row.
            teacher = AbsentTeacher(rawTable[row*COLUMNS+1], rawTable[row*COLUMNS], rawTable[row*COLUMNS+2], rawTable[row*COLUMNS+3], str(self.date.strftime("%m/%-d/%Y")), note)
            absences.append(teacher)

        return absences

    def caseyFriend(self, rawTable: list):
        # Set absences.
        absences = []

        # Figure out the value of the first column.
        while rawTable[0] == '' or 'Absences' in rawTable[0]:
            rawTable.pop(0)

        # Clause #1 - Compact, when name is first column.
        if rawTable[0] == 'Name':
            # Set number of COLUMNS.
            COLUMNS = 6
            # Pop label row.
            for _ in range(COLUMNS):
                rawTable.pop(0)
            # Set number of rows.
            rows = int(len(rawTable)/COLUMNS)

            for row in range(rows):
                # Set note correctly.
                if rawTable[row*COLUMNS+1] == '':
                    note = None
                else:
                    note = rawTable[row*COLUMNS+1]
                # Split the name.
                name = rawTable[row*COLUMNS].split(", ")
                # Generate AbsentTeacher object for row.
                teacher = AbsentTeacher(name[1], name[0], rawTable[row*COLUMNS+3], str(self.date.strftime("%m/%-d/%Y")), note)
                absences.append(teacher)

        # Clause #2 - Standard, with position as first column, 8 columns, and DoW as last.
        elif rawTable[0] == 'Position' and rawTable[5] == 'DoW':
            # Set number of columns.
            COLUMNS = 8
            # Pop label row.
            for _ in range(COLUMNS):
                rawTable.pop(0)
            # Set number of rows.
            rows = int(len(rawTable)/COLUMNS)
            for row in range(rows):
                # Set note correctly.
                if rawTable[row*COLUMNS+3] == '':
                    note = None
                else:
                    note = rawTable[row*COLUMNS+3]
                # Generate AbsentTeacher object for row.
                teacher = AbsentTeacher(rawTable[row*COLUMNS+2], rawTable[row*COLUMNS+1], rawTable[row*COLUMNS+4], str(self.date.strftime("%m/%-d/%Y")), note)
                absences.append(teacher)
        
        # Clause #3 - Short, same as #2 without DoW.
        elif rawTable[0] == 'Position' and rawTable[4] == 'Day':
            # Set number of columns.
            COLUMNS = 7
            # Pop label row.
            for _ in range(COLUMNS):
                rawTable.pop(0)
            # Set number of rows.
            rows = int(len(rawTable)/COLUMNS)
            for row in range(rows):
                # Set the note correctly.
                if rawTable[row*COLUMNS+3] == '':
                    note = None
                else:
                    note = rawTable[row*COLUMNS+3]
                # Generate AbsentTeacher object for row.
                teacher = AbsentTeacher(rawTable[row*COLUMNS+2], rawTable[row*COLUMNS+1], rawTable[row*COLUMNS+4], str(self.date.strftime("%m/%-d/%Y")), note)
                absences.append(teacher)

        return absences

    def tracyConnolly(self, rawTable: list):
        # Set number of columns.
        COLUMNS = 7
        # Absence list.
        absences = []
        # Calculate number of rows.
        rows = int(len(rawTable)/COLUMNS)

        for row in range(rows):
            # Set the note correctly.
            if rawTable[row*COLUMNS+4] == '':
                note = None
            else:
                note = rawTable[row*COLUMNS+4]
            # Generate AbsentTeacher for row.
            teacher = AbsentTeacher(rawTable[row*COLUMNS+1], rawTable[row*COLUMNS], rawTable[row*COLUMNS+2], str(self.date.strftime("%m/%-d/%Y")), note)
            absences.append(teacher)

        return absences