import statistics
import csv
from fuzzywuzzy import fuzz
from typing import Tuple
from dataTypes import structs

class ColumnDetection:
    def __init__(self, school: structs.SchoolName):
        pass
    
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
        if fuzz.ratio(first.lower(), second.lower()) > .9:
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

    def columnConfidence(self, column: list) -> dict[structs.TableColumn: int]:
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

        NOTE_KEYWORDS = ["cancelled", "canceled", "block", "schoology", "classes", "as usual", ""]
        POSITION_KEYWORDS = ["Teacher", "Counselor"]
        LENGTH_KEYWORDS = ["All Day", "Partial Day AM", "Partial Day PM", "Partial Day", "Partial AM", "Partial PM"]
        WEEKDAY_KEYWORDS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "MON", "TUES", "WEDS", "THURS", "FRI", "SAT", "SUN"]
        
        contentPoints = 5 / len(column)

        # TITLE CHECKS
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

            # CONTENT CHECKS
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
        return confidence

    def mapColumns(self, table: structs.RawUpdate) -> dict[tuple]:
        #print(table.content)
        
        confidences = []
        map = {
            structs.TableColumn.FIRST_NAME: (-1, -1),
            structs.TableColumn.LAST_NAME: (-1, -1),
            structs.TableColumn.CS_NAME: (-1, -1),
            structs.TableColumn.WEEKDAY: (-1, -1),
            structs.TableColumn.DATE: (-1, -1),
            structs.TableColumn.NOTE: (-1, -1),
            structs.TableColumn.LENGTH: (-1, -1),
            structs.TableColumn.POSITION: (-1, -1),
        }

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
                    maxKey = max(col, key=col.get)
                    if col[maxKey] != 0 and col[maxKey] > map[maxKey][1]:
                        map[maxKey] = (i, col[maxKey])
                        break
                    else:
                        del col[maxKey]
        return map
        
        
        
        

            
        


                

                                
        

        