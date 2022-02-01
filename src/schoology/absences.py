from datetime import datetime
from typing import List
from dataTypes import structs, schemas, models
import schoolopy
from .columnDetection import ColumnDetection
from database.database import SessionLocal
import database.crud as crud

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
        self.db = SessionLocal()

    # Gets the feed, accepting an argument 'school' which is either 0 or 1, 0 corresponding to North and 1 corresponding to South (this value being the same as the school's index within the API array). Grabs all updates posted by individuals of interest and saves them to an array 'feed', and returns that array.
    def getFeed(self, school: structs.SchoolName):
        teachers = ["Tracy Connolly", "Casey Friend", "Suzanne Spirito"]
        feed = []
        for update in reversed(self.api[school].get_feed()):
            user = self.api[school].get_user(update.uid)
            if user.name_display in teachers:
                feed.append((user.name_display, update.body, update.last_updated))
        return feed

    # Gets the absence table for the date requested as defined by 'date'. Returns just this update for furthing processing. The date argument ultimately comes from the call of this function in main.py.
    def getCurrentTable(self, school: structs.SchoolName):
        feed = self.getFeed(school)
        for poster, body, date in feed:
            postDate = datetime.utcfromtimestamp(int(date))
            if self.date.date() == postDate.date():
                return structs.RawUpdate(content=body.split("\n"), poster=poster)
        return None

    # Takes the raw North attendance table from the prior function and parses it, using the AbsentTeacher dataclass. Returns an array of entries utilizing this class. 
    def filterAbsencesNorth(self, date):       
        self.date = date
        table = self.getCurrentTable(structs.SchoolName.NEWTON_NORTH)  
        absences = ContentParser(date).parse(table, structs.SchoolName.NEWTON_NORTH)
        print(absences)
        for absence in absences:
            crud.addAbsence(self.db, absence)
        return absences

    # Same as the above, but the parsing is handled slightly differently due to the South absence table being differenct in formatting.
    def filterAbsencesSouth(self, date):
        self.date = date
        table = self.getCurrentTable(structs.SchoolName.NEWTON_SOUTH)    
        absences = ContentParser(date).parse(table, structs.SchoolName.NEWTON_SOUTH)
        print(absences)
        for absence in absences:
            crud.addAbsence(self.db, absence)
        return absences

class ContentParser:
    def __init__(self, date):
        self.date = date
    
    def parse(self, update: structs.RawUpdate, school: structs.SchoolName) -> List[schemas.AbsenceCreate]:

        if update == [] or None:
            return None
        if school == structs.SchoolName.NEWTON_NORTH:
            detection = ColumnDetection(structs.SchoolName.NEWTON_NORTH)
            update = self.deriveTable(update)
            update.columns = detection.countColumns(update.content)[0]
            update.content = [update.content[i:i+update.columns] for i in range(0,len(update.content),update.columns)]
            map = detection.mapColumns(update)
            obj = self.constructObject(update, map, structs.SchoolName.NEWTON_NORTH)
            return obj

        elif school == structs.SchoolName.NEWTON_SOUTH:
            detection = ColumnDetection(structs.SchoolName.NEWTON_SOUTH)
            update.columns = detection.countColumns(update.content)[0]
            update.content = [update.content[i:i+update.columns] for i in range(0,len(update.content),update.columns)]
            map = detection.mapColumns(update)
            obj = self.constructObject(update, map, structs.SchoolName.NEWTON_SOUTH)
            return obj

    def constructObject(self, update: structs.RawUpdate, map: dict, school: structs.SchoolName) -> List[schemas.AbsenceCreate]:
        objList = []
        print(update)
        for row in update.content:

            try:
                teacher = schemas.TeacherCreate(first=row[map[structs.TableColumn.FIRST_NAME][0]], last=row[map[structs.TableColumn.LAST_NAME][0]], school=school)
            except IndexError:
                continue

            try:
                length = row[map[structs.TableColumn.LENGTH][0]]
            except IndexError:
                length = None

            try:
                note = row[map[structs.TableColumn.NOTE][0]]
                if note in ["", "\r", "\n"]:
                    note = None
            except IndexError:
                note = None

            object = schemas.AbsenceCreate(
                teacher = teacher,
                length = length,
                note = note
                )

            objList.append(object)
        return objList

    def deriveTable(self, update: structs.RawUpdate) -> structs.RawUpdate:
        while ('position' or 'name') not in update.content[0].lower():
            update.content.pop(0)
        return update
