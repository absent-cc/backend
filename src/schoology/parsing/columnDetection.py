import statistics
import csv
import Levenshtein as lev
from typing import Tuple
from dataTypes import structs

class ColumnDetection:
    def __init__(self, school: structs.SchoolName):

        self.teacherFirsts = set()
        self.teacherLasts = set()

        with open(f'data/{school}_teachers.csv', 'r') as f:
            csvF = csv.DictReader(f)
            for col in csvF:
                self.teacherFirsts.add(col['first'])
                self.teacherLasts.add(col['last'])

    def countColumns(self, table: list) -> Tuple[int, float]:
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

    def isDate(self, dateStr: str) -> bool:
        splitDate = dateStr.split("/")
        if len(splitDate) != 3:
            return False

        for segment in splitDate:
            if not segment.isnumeric():
                return False

        return True
    
    def isFuzzyMatch(self, first: str, second: str) -> bool:
        if lev.ratio(first.lower(), second.lower()) > .9:
            return True
        return False
    
    def isFirst(self, name: str) -> bool:
        for first in self.teacherFirsts:
            if self.isFuzzyMatch(name, first):
                return True
        return False

    def isLast(self, name: str) -> bool:
        for last in self.teacherLasts:
            if self.isFuzzyMatch(name, last):
                return True
        return False

    def columnConfidence(self, column: list):
        confidence = {
            "first": 0,
            "last": 0,
            "cs": 0,
            "weekday": 0,
            "date": 0,
            "note": 0,
            "length": 0,
            "position": 0,
        }

        DATE_TITLE = ["Date"]
        POSITION_TITLE = ["Position"]
        NOTE_TITLE = ["Notes", "Notes to Student"]
        CS_TITLE = ["Name"]
        FIRST_TITLE = ["First Name", "First"]
        LAST_TITLE = ["Last Name", "Last"]
        LENGTH_TITLE = ["Day"]
        WEEKDAY_TITLE = ["DoW", "Day of Week", "D o W", "D of W"]

        NOTE_KEYWORDS = ["cancelled", "canceled", "block", "schoology", "classes", "as usual", ""]
        POSITION_KEYWORDS = ["Teacher", "Counselor"]
        LENGTH_KEYWORDS = ["All Day", "Partial Day AM", "Partial Day PM", "Partial Day", "Partial AM", "Partial PM"]
        WEEKDAY_KEYWORDS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "MON", "TUES", "WEDS", "THURS", "FRI", "SAT", "SUN"]
        
        contentPoints = 5 / len(column)

        # TITLE CHECKS
        for i, item in enumerate(column):
            if i == 0:
                points = 1.5
            else:
                points = 1

            for entry in FIRST_TITLE:
                if self.isFuzzyMatch(item, entry):
                    confidence["first"] += points
            for entry in LAST_TITLE:
                if self.isFuzzyMatch(item, entry):
                    confidence["last"] += points
            for entry in POSITION_TITLE:
                if self.isFuzzyMatch(item, entry):
                    confidence["position"] += points
            for entry in CS_TITLE:
                if self.isFuzzyMatch(item, entry):
                    confidence["cs"] += points
            for entry in LENGTH_TITLE:
                if self.isFuzzyMatch(item, entry):
                    confidence["length"] += points
            for entry in WEEKDAY_TITLE:
                if self.isFuzzyMatch(item, entry):
                    confidence["weekday"] += points
            for entry in NOTE_TITLE:
                if self.isFuzzyMatch(item, entry):
                    confidence["note"] += points
            for entry in DATE_TITLE:
                if self.isFuzzyMatch(item, entry):
                    confidence["date"] += points

            # CONTENT CHECKS
            if self.isFirst(item):
                confidence["first"] += contentPoints
            if self.isLast(item):
                confidence["last"] += contentPoints
            if self.isDate(item):
                confidence["date"] += contentPoints
            for entry in POSITION_KEYWORDS:
                if entry in item:
                    confidence["position"] += contentPoints
            for entry in NOTE_KEYWORDS:
                if self.isFuzzyMatch(item, entry):
                    confidence["note"] += contentPoints
            for entry in LENGTH_KEYWORDS:
                if self.isFuzzyMatch(item, entry):
                    confidence["length"] += contentPoints
            for entry in WEEKDAY_KEYWORDS:
                if self.isFuzzyMatch(item, entry):
                    confidence["weekday"] += contentPoints
        return confidence

    def mapColums(self, table: structs.RawUpdate):
        #print(table.content)
        
        confidences = {}
        map = {}
        for col in range(table.columns - 2):
            
            column = []
            for row in table.content:
                print(row, col)
                column.append(row[col]) 

            colConfidence = self.columnConfidence(column)
            confidences[col] = colConfidence

        
        

            
        


                

                                
        

        