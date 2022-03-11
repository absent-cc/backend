import csv as c
import statistics
from typing import Dict, Tuple

from fuzzywuzzy import fuzz

from ..dataTypes import structs
FUZZY_MATCH_THRESHOLD = 90

class ColumnDetection:
    def __init__(self, school: structs.SchoolName):
    
        self.FIRSTS = [] # List that stores all FIRST names of teachers @ school
        self.LASTS = [] # List that stores all LAST names of teachers @ school

        # Get list of all teachers @ South or North
        with open(f'data/{school}_teachers.csv') as f:
            csv = c.DictReader(f)
            for col in csv:
                self.FIRSTS.append(col['First'])
                self.LASTS.append(col['Last'])

    # Function that dynamically counts the number of columns in a schoology absence table
    def countColumns(self, table: list) -> Tuple[int, float]:
        lineBreaks = [i for i, x in enumerate(table) if x in ["", "\r", "\n",]] # Generates list of linebreaks and their indexes.
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

    # Checks if a string is a date.
    def isDate(self, dateStr: str) -> bool:
        splitDate = dateStr.split("/")
        if len(splitDate) != 3: # If there are not 3 parts, it is not a date.
            return False

        for segment in splitDate:
            if not segment.isnumeric(): # Makes sure components are all numbers.
                return False

        return True
    
    # Checks if two strings are similar.
    def isFuzzyMatch(self, first: str, second: str) -> bool:
        if fuzz.ratio(first.lower(), second.lower()) > FUZZY_MATCH_THRESHOLD: # Threshold for fuzzy matching is 90%
            return True
        return False
    
    # Calculates the confidence of whether or not a column is a bunch of FIRST names
    def isFirst(self, name: str) -> bool:
        for first in self.FIRSTS:
            if self.isFuzzyMatch(name, first):
                return True
        return False

    # Calculates the confidence of whether or not a column is a bunch of LAST names
    def isLast(self, name: str) -> bool:
        for last in self.LASTS:
            if self.isFuzzyMatch(name, last):
                return True
        return False

    # Gets the confidences of each column.
    def columnConfidence(self, column: list) -> Dict[structs.TableColumn, int]:
        confidence = {
            structs.TableColumn.FIRST_NAME: 0,
            structs.TableColumn.LAST_NAME: 0,
            structs.TableColumn.CS_NAME: 0,
            structs.TableColumn.WEEKDAY: 0,
            structs.TableColumn.DATE: 0,
            structs.TableColumn.NOTE: 0,
            structs.TableColumn.LENGTH: 0,
            structs.TableColumn.POSITION: 0,
        }
        
        NOTE_KEYWORDS = ["cancelled", "canceled", "block", "schoology", "classes", "as usual", "", "\r", "\n", "\xa0"] # Keywords that usually appear in notes
        POSITION_KEYWORDS = ["Teacher", "Counselor"] # Keywords that usually appear in position
        LENGTH_KEYWORDS = ["All Day", "Partial Day AM", "Partial Day PM", "Partial Day", "Partial AM", "Partial PM"] # Keywords that usually appear in length of absence
        WEEKDAY_KEYWORDS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "MON", "TUES", "WEDS", "THURS", "FRI", "SAT", "SUN"] # Keywords that usually appear in weekday
        CS_NAME_KEYWORDS = [',']
        contentPoints = 5 / len(column)
        csPossibilites = set()
        # Title Of Column Check
        for i, item in enumerate(column):
            if i == 0:
                points = 2.5
            else:
                points = 1.0

            if item == structs.TableColumn.FIRST_NAME:
                confidence[structs.TableColumn.FIRST_NAME] += points
            if item == structs.TableColumn.LAST_NAME:
                confidence[structs.TableColumn.LAST_NAME] += points
            if item == structs.TableColumn.POSITION:
                confidence[structs.TableColumn.POSITION] += points 
            if item == structs.TableColumn.CS_NAME:
                confidence[structs.TableColumn.CS_NAME] += points 
            if item == structs.TableColumn.WEEKDAY:
                confidence[structs.TableColumn.WEEKDAY] += points 
            if item == structs.TableColumn.NOTE:
                confidence[structs.TableColumn.NOTE] += points
            if item == structs.TableColumn.DATE:
                confidence[structs.TableColumn.DATE] += points 
            if item == structs.TableColumn.LENGTH:
                confidence[structs.TableColumn.LENGTH] += points 

            # Content Confidence Check
            if self.isFirst(item):
                confidence[structs.TableColumn.FIRST_NAME] += contentPoints
            if self.isLast(item):
                confidence[structs.TableColumn.LAST_NAME] += contentPoints
            if self.isDate(item):
                confidence[structs.TableColumn.DATE] += contentPoints
            for entry in POSITION_KEYWORDS:
                if entry in item:
                    confidence[structs.TableColumn.POSITION] += contentPoints
            for entry in NOTE_KEYWORDS:
                if self.isFuzzyMatch(item, entry):
                    confidence[structs.TableColumn.NOTE] += contentPoints
            for entry in LENGTH_KEYWORDS:
                if self.isFuzzyMatch(item, entry):
                    confidence[structs.TableColumn.LENGTH] += contentPoints
            for entry in WEEKDAY_KEYWORDS:
                if self.isFuzzyMatch(item, entry):
                    confidence[structs.TableColumn.WEEKDAY] += contentPoints
            for entry in CS_NAME_KEYWORDS:
                if entry in item:
                    confidence[structs.TableColumn.CS_NAME] += contentPoints
            if confidence[structs.TableColumn.CS_NAME] > 0:
                item = item.split(',')
                addition = (-1, -1)
                if len(item) == 2:
                    if self.isFirst(item[0]):
                        addition = (0, -1)
                    elif self.isFirst(item[1]):
                        addition = (1, -1)
                    elif self.isLast(item[0]):
                        addition = (addition[0], 0)
                    elif self.isLast(item[1]):
                        addition[1] = (addition[0], 1)
                    else:
                        confidence[structs.TableColumn.CS_NAME] -= contentPoints
                        addition = (-1, -1)
                    csPossibilites.add(addition)
        locTuple = None
        if csPossibilites != set():
            firstLoc = max(csPossibilites,key=lambda item:item[0])[0]
            lastLoc = max(csPossibilites,key=lambda item:item[1])[1]
            locTuple = (firstLoc, lastLoc)
        return structs.Confidence(confidences=confidence, csMap=locTuple)

    def mapColumns(self, table: structs.RawUpdate) -> Dict[structs.TableColumn, Tuple[int, int]]:
        confidences = []

        map = structs.ColumnMap()
        for col in range(table.columns - 2):
            column = []
            for row in table.content:
                try:
                    column.append(row[col])
                except IndexError:
                    continue 
            colConfidence = self.columnConfidence(column)
            confidences.append(colConfidence)

        oldMap = None
        while map != oldMap:
            oldMap = map
            for i, col in enumerate(confidences):
                for _ in range(8):
                    maxKey = max(col.confidences, key=col.confidences.get)
                    if col.confidences[maxKey] != 0 and col.confidences[maxKey] > map[maxKey][1]:
                        map[maxKey] = (i, col.confidences[maxKey])
                        break
                    else:
                        del col.confidences[maxKey]
        map["CS_MAP"] = confidences[map[structs.TableColumn.CS_NAME][0]].csMap
        return map       
        
        

            
        


                

                                
        

        