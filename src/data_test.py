from uuid import uuid4
from dataStructs import *
from database.databaseHandler import *
from datetime import datetime

long = "a"*86
exampleToken = Token(long)

db = DatabaseHandler(SchoolName.NEWTON_SOUTH)
uuid = uuid4()
exampleSess = Session(uuid, exampleToken, datetime.now())
db.addSession(exampleSess)
db.invalidateSession(exampleSess)

exampleStudent = Student(uuid4(), "your mom", "Kevin", "Yang", SchoolName.NEWTON_SOUTH, 10)
schedule = Schedule()
db.addStudent(exampleStudent, schedule)
