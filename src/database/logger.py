from dataStructs import *
from datetime import datetime 
import os

# Logger to record actions of abSENT
class Logger():
    def __init__(self, path: str = "data/log.txt"):
        self.path = path
        # Check if log file exists
        # If not, create it
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                f.write("TIME | ACTION | DETAILS\n")      

    # Default method for logging
    def log(self, message):
        current_time = datetime.now()
        with open(self.path, 'a') as f:
            f.write(f"{current_time} | {message}\n")

    def systemStartup(self):
        self.log("SYSTEM STARTUP")
    
    # Log when new student is added to database
    def addedStudent(self, user: Student):
        self.log(f"STUDENT ADDED \t| {user.first}; {user.last}; {user.number}")

    # Log when student is removed from database    
    def removedStudent(self, user: Student):
        self.log(f"STUDENT REMOVED \t| {user.first}; {user.last}; {user.number}")
    
    # Log when a new teacher is added to database
    def addedTeacher(self, teacher: Teacher):
        self.log(f"TEACHER ADDED \t| {teacher.first}; {teacher.last}")
    
    # Log when a teacher is removed from database
    def removedTeacher(self, teacher: Teacher):
        self.log(f"TEACHER REMOVED \t| {teacher.first}; {teacher.last}")

    def editSchedule(self, user: Student, enumBlock: SchoolBlock, teacher: Teacher):
        self.log(f"USER SCHEDULE EDITED \t| {user.id}; {enumBlock}; {str(teacher)}")

    def schoolgyGrabAbsences(self, school: SchoolName):
        self.log(f"PULLED ABSENCES \t | {school}")
    
    def noDataAvailable(self):
        self.log("ABSENT DATA NOT AVAILABLE")

    def sentAbsencesNotification(self, user: Student):
        if user == None:
            self.log(f"SENT ABSENCES NOTIFICATIONS \t| NONE")
        else:
            self.log(f"SENT ABSENCES NOTIFICATIONS \t| {user.id}")

    def sentAbsencesSuccess(self, school: SchoolName):
        self.log(f"SENT ABSENCES SUCCESS \t| {school}")

    def noUsersToNotify(self):
        self.log("SENT ABSENCES NOTIFICATIONS \t| NO USERS TO NOTIFY")
    
    def resetSchoologyCheck(self):
        self.log(f"SCHOOLGY CHECK RESET")
    
    def schoologyOffDay(self, day: str):
        self.log(f"abSENT OFF DAY \t| {day}")
    
    def adminLogin(self, number: str):
        self.log(f"ADMIN LOGIN \t| {number}")
    
    def adminAnnounce(self, number: str, message: str, school: SchoolName, grade: int):
        self.log(f"ADMIN ANNOUNCE \t| {number}; {message}; {str(school)}; {grade}")

    def adminTimeout(self, number: str):
        self.log(f"ADMIN TIME OUT \t| {number}")
    
    def sqlInjectionAttempted(self, number: str):
        self.log(f"SQL INJECTION ATTEMPTED \t| {number}")
    
    def canceledService(self, user: Student):
        self.log(f"SERVICE CANCELED \t| {user.id}; {user.first}; {user.last}; {user.number}")
    
    def accountSetupStarted(self, number: str):
        self.log(f"ACCOUNT SETUP STARTED \t| {number}")

    def accountSetupFinished(self, number: str):
        self.log(f"ACCOUNT SETUP FINISHED \t| {number}")
    
    # Method to reset log file
    def resetLog(self):
        with open(self.path, 'w') as f:
            f.write("TIME | ACTION | DETAILS\n")

class MessageLogger():
    def __init__(self, path: str = "data/messageLog.txt"):
        self.path = path

        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                f.write("TIME \t| SENDER \t| RECEIVER \t| MESSAGE\n")
    
    # Default method for logging
    def log(self, sender_number: str, receiver_number: str, message: str):
        current_time = datetime.now()
        with open(self.path, 'a') as f:
            f.write(f"{current_time.strftime('%d/%m/%Y %H:%M:%S')} | {sender_number} \t| {receiver_number} \t| {message}\n")

    # Method to reset log file
    def resetLog(self):
        with open(self.path, 'w') as f:
            f.write("TIME | SENDER | RECEIVER | MESSAGE\n")

