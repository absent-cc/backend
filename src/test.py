from uuid import uuid4
import uvicorn
from dataStructs import *
from database.databaseHandler import DatabaseHandler

database = DatabaseHandler()

if __name__ == "__main__":
    uvicorn.run("api.v1:absent", host="0.0.0.0", port=8081, reload=True)

student = Student(uuid4(), "TestSubject", "Roshan", "Karim", SchoolName.NEWTON_NORTH, 10)
#database.addStudentToStudentDirectory(student)
