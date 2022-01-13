from pydantic.errors import ArbitraryTypeError
from dataStructs import *
import sqlite3
from database.logger import Logger
import random
from typing import List

class DatabaseHandler():
    def __init__(self, db_path = "abSENT.db"):
        self.db_path = f"data/{db_path}"
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        create_student_directory = """
        CREATE TABLE IF NOT EXISTS student_directory (
                uid TEXT PRIMARY KEY,
                gid TEXT,
                first TEXT,
                last TEXT,
                school TEXT,
                grade TEXT
            )
            """
        create_teacher_directory = """
        CREATE TABLE IF NOT EXISTS teacher_directory (
                tid INTEGER PRIMARY KEY AUTOINCREMENT,
                first TEXT,
                last TEXT,
                school TEXT
            )
            """
        create_classes_NSHS = """
        CREATE TABLE IF NOT EXISTS classes_NSHS (
                tid INTEGER,
                block TEXT,
                uid TEXT,
                FOREIGN KEY(uid) 
                    REFERENCES student_directory(uid)
                FOREIGN KEY(tid) 
                    REFERENCES teacher_directory(tid)
                PRIMARY KEY(tid, block, uid)
            )
            """
        create_classes_NNHS = """
        CREATE TABLE IF NOT EXISTS classes_NNHS (
                tid INTEGER,
                block TEXT,
                uid TEXT,
                FOREIGN KEY(uid) 
                    REFERENCES student_directory(uid)
                FOREIGN KEY(tid) 
                    REFERENCES teacher_directory(tid)
                PRIMARY KEY(tid, block, uid)
            )
            """
        create_sessions = """
        CREATE TABLE IF NOT EXISTS sessions (
                cid TEXT PRIMARY KEY,
                start_time TEXT,
                validity INT
                )
                """
        
        # Create tables if they don't exist
        self.cursor.execute(create_student_directory)
        self.cursor.execute(create_teacher_directory)
        self.cursor.execute(create_classes_NNHS)
        self.cursor.execute(create_classes_NSHS)
        self.cursor.execute(create_sessions)

        self.connection.commit()

        # Logging:
        self.logger = Logger()
    
    # Reset the database, for development purposes only!
    def reset(self):
        import os
        # If the database exists, delete it
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    #
    # STUDENT AND TEACHER MANAGEMENT - GET
    #

    # Get teacher object from DB based off of inputted teacher
    def getTeacher(self, teacher: Teacher):
        # Check if teacher object already has an id
        if teacher.tid == None:
            # If not, search teachers in DB by first + last name
            query = f"SELECT * FROM teacher_directory WHERE first = ? AND last = ? AND school = ? LIMIT 1"
            args = (teacher.first, teacher.last, teacher.school)
        else:
            # If teacher object already has an id, search teachers in DB by id
            query = f"SELECT * FROM teacher_directory WHERE id = ? LIMIT 1"
            args = (teacher.tid,)
        # Conduct query
        res = self.cursor.execute(query, args).fetchone()
        # If teacher is found (not None), return teacher object
        if res != None:
            teacher = Teacher(first=res[1], last=res[2], school=SchoolNameMapper()[res[3]], tid=res[0])
            return teacher
        return None
    
    # Get student object from DB based off of inputted student
    def getStudent(self, student: Student):
        # Check if student object already has an id
        if student.uid == None:
            # If not, search students in DB by gid.
            query = "SELECT * FROM student_directory WHERE gid = ? LIMIT 1"
            args = (str(student.gid),)
        else:
            # If student object already has an id, search students in DB by id
            query = "SELECT * FROM student_directory WHERE uid = ? LIMIT 1"
            args = (str(student.uid),)
        # Conduct query
        res = self.cursor.execute(query, args).fetchone()
        # If student is found (not None), return student object
        if res != None:
            student = Student(uid=res[0], gid=res[1], first=res[2], last=res[3], school=SchoolNameMapper()[res[4]], grade=res[5])
            return student
        return None
    
    # Get teacher id from DB based off of inputted teacher
    ## Used to check if a teacher is in DB or not
    def getTeacherID(self, teacher: Teacher):
        # Check if teacher object already has an id
        if teacher.tid == None:
            # If not, search teachers in DB by first + last name
            query = "SELECT tid FROM teacher_directory WHERE first = ? AND last = ? LIMIT 1"
            args = (teacher.first, teacher.last)
            # Conduct query
            res = self.cursor.execute(query, args).fetchone()
            # If teacher is found (not None), return teacher id (first in results list)
            if res != None:
                return res[0]
            else:
                return None
        else:
            # If teacher object already has an id, return id
            return teacher.tid
    
    # Get student id from DB based off of inputted student
    ## Used to check if a student is in DB or not
    def getStudentID(self, student: Student):
        # Check if student object already has an id
        if student.uid == None:
            # If not, search students in DB by gid
            query = "SELECT uid FROM student_directory WHERE gid = ? LIMIT 1"
            args = (str(student.gid),)
            # Conduct queryz
            res = self.cursor.execute(query, args).fetchone()
            # If student is found (not None), return student id (first in results list)
            if res != None:
                return res[0]
            else:
                return None
        else:
            # If student object already has an id, return id
            return student.uid
    
    # DEP
    def getClassID(self, teacher: Teacher, block: SchoolBlock, student: Student) -> int:
        # Classes are defined by a teacher, block, and student
        
        if student.school == None:
            return None

        # Grab teacher id if it isn't given
        if teacher.tid == None:
            teacher.tid = self.getTeacherID(teacher)
        
        # Grab student id if it isn't given
        if student.uid == None:
            student.uid = self.getStudentID(student)

        query = f"SELECT clid FROM classes_{student.school} WHERE tid = ? AND block = ? AND uid = ? LIMIT 1"
        args = (teacher.tid, BlockMapper()[block], str(student.uid))
        res = self.cursor.execute(query, args).fetchone()
        if res != None:
            return res[0]
        return None
        
    # Get student objects of a given grade, return as list.
    def getStudentsByGrade(self, grade: int) -> list:
        query = "SELECT * FROM student_directory WHERE grade = ?"
        args = (grade,)
        res = self.cursor.execute(query, args).fetchall()
        studentArray = []
        for col in res:
            # Mapping attributes from student DB to a student dataclass.
            entry = Student(uid=col[0], gid=col[1], first=col[2], last=col[3], school=SchoolNameMapper()[col[4]], grade=col[5])
            studentArray.append(entry)
        return studentArray

    # Just grabs all students, returns list.
    def getStudents(self) -> list:
        query = "SELECT * FROM student_directory"
        res = self.cursor.execute(query).fetchall()
        studentArray = []
        for col in res:
            entry = Student(uid=col[0], gid=col[1], first=col[2], last=col[3], school=SchoolNameMapper()[col[4]], grade=col[5])
            studentArray.append(entry)
        return studentArray

    # Gets a list of students by absent teacher.
    def getStudentsByAbsentTeacher(self, teacher: Teacher, block: SchoolBlock, school: SchoolName) -> List[Student]:
        tid = self.getTeacherID(teacher)
        if tid == None:
            return []
        strBlock = BlockMapper()[block]
        strSchool = SchoolNameMapper()[school]

        query = f"""
        SELECT *
        FROM student_directory
        WHERE uid IN (
            SELECT uid
            FROM classes_{teacher.school}
            WHERE tid = ? AND block = ? AND school = ?
        )
        """
        args = (tid, strBlock, strSchool)
        res = self.cursor.execute(query, args).fetchall()
        students = []
        for col in res:
            students.append(Student(uid=col[0], gid=col[1], first=col[2], last=col[3], school=SchoolNameMapper()[col[4]], grade=col[5]))
        return students

    # Gets schedule, builds schedule object for a given student.
    def getScheduleByStudent(self, student: Student):
        teachers = self.getTeachersFromStudent(student)
        schedule = Schedule()
        if student.school == None:
            return None
        # Query teacher objects for blocks and generate schedule.
        for teacher in teachers:
            query = f"""
            SELECT block
            FROM classes_{student.school}
            WHERE tid = ? AND uid = ?
            """
            args = (teacher.tid, str(student.uid))
            res = self.cursor.execute(query, args).fetchall()
            for block in res:
                blockTeachers = getattr(schedule, block[0])
                if blockTeachers != None and not isinstance(blockTeachers, NotPresent):
                    buildAppend = getattr(schedule, block[0])
                    buildAppend.append(teacher)
                    setattr(schedule, block[0], buildAppend)
                else:
                    setattr(schedule, block[0], [teacher])

        for block in schedule:
            if isinstance(block[1], NotPresent):
                setattr(schedule, block[0], None)

        return schedule
    
    def getTeachersFromStudent(self, student: Student):
        if student.school == None:
            return None
        # Get raw teacher data by student.
        if student.uid == None:
            return None
        query = f"""
        SELECT *
        FROM teacher_directory
        WHERE tid in (
            SELECT tid
            FROM classes_{student.school}
            WHERE uid = ?
        )
        """
        args = (str(student.uid),)
        res = self.cursor.execute(query, args).fetchall()
        teachers = []
        # Create teacher objects.
        for teacher in res:
            teachers.append(Teacher(first=teacher[1], last=teacher[2], school=SchoolNameMapper()[teacher[3]], tid=teacher[0]))
        return teachers

    #
    # STUDENT AND TEACHER MANAGEMENT - ADD
    #

    def addStudentSchedule(self, student: Student, oldSchedule: Schedule, schedule: Schedule) -> bool:
        if student.uid == None:
            student.uid = self.getStudentID(student)
            if student.uid == None:
                return False
        for block in schedule:
            teachers = block[1]
            if isinstance(teachers, NotPresent):
                teachers = getattr(oldSchedule, block[0])
            if teachers != None and not isinstance(teachers, NotPresent):
                for teacher in teachers:
                    self.addClass(student, block[0], Teacher(first=teacher.first, last=teacher.last, school=teacher.school))
        return True

    # Add student to student directory
    ## Does not check whether or not student is already in DB, assumes not
    def addStudent(self, student: Student):
        # Insert student into student directory
        query = """
        INSERT INTO student_directory(uid, gid, first, last, school, grade) VALUES (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
            )
        """
        args = (str(student.uid), str(student.gid), student.first, student.last, student.school, student.grade)
        # Conduct insertion
        self.cursor.execute(query, args)
        self.connection.commit()

        self.logger.addedStudent(student)
        # Return the newly generated id for student object manipulation
        return student.uid

    # Add teacher to teacher directory
    ## Does not check whether or not teacher is already in DB, assumes not
    def addTeacher(self, teacher: Teacher):
        # Insert teacher into teacher directory
        query = """
        INSERT INTO teacher_directory(
                first, 
                last, 
                school)
            VALUES (
                ?,
                ?,
                ?
            )
        """
        args = (teacher.first.upper(), teacher.last.upper(), teacher.school)
        # Conduct insertion
        self.cursor.execute(query, args)
        query = "SELECT last_insert_rowid()"
        return_id = self.cursor.execute(query)
        tid = return_id.fetchone()[0] # Get teacher id created from autoincrement

        self.connection.commit()

        self.logger.addedTeacher(teacher)

        return tid

    def addClass(self, student: Student, block: SchoolBlock, newTeacher: Teacher):
        if student.school == None:
            return False
        # Get teacher id
        if newTeacher.tid == None:
            newTeacher.tid = self.getTeacherID(newTeacher)
            if newTeacher.tid == None:
                newTeacher.tid = self.addTeacher(newTeacher)
        # Get student id
        if student.uid == None:
            student.uid = self.getStudentID(student)
        # Get block ENUM
        # Add class to classes table
        query = f"""
        INSERT INTO classes_{student.school}(tid, block, uid) VALUES (
            ?,
            ?,
            ?
            ) 
        """
        args = (newTeacher.tid, block, str(student.uid))
        self.cursor.execute(query, args)
        self.connection.commit()
        return True

    #
    # STUDENT AND TEACHER MANAGEMENT - REMOVE
    #

    # Remove student from student directory
    def removeStudentFromStudentDirectory(self, student: Student) -> bool:
        # You can only remove student if there is a student id 
        if student.uid == None:
            return False
        # Remove student from student directory
        query = "DELETE FROM student_directory WHERE sid = ?"
        args = (str(student.uid),)
        self.cursor.execute(query, args)
        self.connection.commit()
        return True

    # Removes student from DB.
    def removeStudent(self, student: Student) -> bool:
        if student.uid == None:
            return False
        if student.school == None:
            return False
        # Delete a student's classes.
        query = f"DELETE FROM classes_{student.school} WHERE uid = ?"
        args = (str(student.uid),)
        self.cursor.execute(query, args)
        self.connection.commit
        self.removeStudentFromStudentDirectory(student)
        return True
    
    # Remove class from classes table
    def removeClass(self, teacher: Teacher, block: SchoolBlock, student: Student) -> bool:
        if student.school == None:
            return False
        if teacher.tid == None or block == None or student.uid == None:
            return False
        
        query = f"DELETE FROM classes_{student.school} WHERE tid = ? AND block = ? and uid = ?"
        args = (teacher.tid, block, student.uid)
        self.cursor.execute(query, args)
        self.connection.commit()
        return True
        
    def removeStudentSchedule(self, student):
        if student.uid == None:
            student.uid == self.getStudentID(student)
            if student.uid == None:
                return False
        if student.school == None:
            return False

        query = f"DELETE FROM classes_{student.school} WHERE uid = ?"
        args = (str(student.uid),)
        self.cursor.execute(query, args)
        self.connection.commit()
        return True

    #
    # STUDENT AND TEACHER MANAGEMENT - UPDATE
    #

    def updateStudentClasses(self, student, schedule): 
        
        if student.school == None:
            return False

        oldSchedule = self.getScheduleByStudent(student)
        self.removeStudentSchedule(student)
        self.addStudentSchedule(student, oldSchedule, schedule)

        return True        
        # currentSchedule = self.getScheduleByStudent(student)
        # if currentSchedule == None:
        #     currentSchedule = Schedule()

        # print(currentSchedule)
        # print(schedule)

        # for block in schedule:
        #     if schedule[block] == None:
        #         if currentSchedule[block] == None:
        #             continue
        #         for teacher in currentSchedule[block]:
        #             self.removeClass(teacher, block, student)
        #     else:
        #         if currentSchedule[block] == None:
        #             for teacher in schedule[block]:
        #                 self.addClass(student, block, teacher)
        #             continue
        #         diff = int(len(schedule[block]) - len(currentSchedule[block]))
        #         newSetIter = iter(schedule[block])
        #         oldSetIter = iter(currentSchedule[block])
                
        #         if diff > 0:
        #             for _ in range(diff):
        #                 newTeacher = next(newSetIter)
        #                 self.addClass(student, block, newTeacher)
        #             for teacher in currentSchedule[block]:
        #                 oldTeacher = next(oldSetIter)
        #                 self.changeClass(student, oldTeacher, block, teacher)
        #         elif diff < 0:
        #             for _ in range(abs(diff)):
        #                 oldTeacher = next(oldSetIter)
        #                 print("REMOVED", oldTeacher)
        #                 self.removeClass(student, block, oldTeacher)
        #             for teacher in schedule[block]:
        #                 oldTeacher = next(oldSetIter)
        #                 print("REPLACED", oldTeacher)
        #                 self.changeClass(student, oldTeacher, block, teacher)
        #         elif diff == 0:
        #             for teacher in schedule[block]:
        #                 oldTeacher = next(oldSetIter)
        #                 self.changeClass(student, oldTeacher, block, teacher)
    
    # Change existing class entry in data table classes
    def updateClass(self, student: Student, old_teacher: Teacher, block: SchoolBlock, new_teacher: Teacher) -> bool:
        if student.school == None:
            return None
        # Map enum SchoolBlock to string savable to DB
        str_block = BlockMapper()[block]
        
        # If teacher is none type, delete specific entry for changing
        ## Note: abSENT does not store the lack of a class in the DB
        if new_teacher == None:
            if student.uid == None:
                student.uid = self.getStudentID(student)
            query = f"""
            DELETE FROM classes_{student.school} WHERE tid = ? AND block = ? AND uid = ?
            """
            args = (old_teacher.tid, str_block, str(student.uid))
            self.cursor.execute(query, args)
            self.connection.commit()
            return True

        # Grab teacher id from DB
        tid = self.getTeacherID(new_teacher)

        # If teacher id is none, then teacher does not exist
        # Add that teacher to directory
        if tid == None:
            tid = self.addTeacherToTeacherDirectory(new_teacher)
        
        if student.uid != None:
            # Get teacher id for the given block and student. 
            query = f"""
            SELECT tid
            FROM classes_{student.school}
            WHERE tid = ? AND block = ? AND uid = ?
            """
            args = (old_teacher.tid, str_block, str(student.uid))
            res = self.cursor.execute(query, args).fetchone()
            # If student has an empty block, we can just add this teacher to the directory.
            if res == None:
                self.addClass(tid, block, student.uid)
            # Else class slot full, update the class entry that already exists.
            else:
                query = f"""
                UPDATE classes_{student.school}
                SET tid = ?
                WHERE tid = ? AND block = ? AND uid = ?
                """
                args = (tid, res[0], str_block, str(student.uid))
                self.cursor.execute(query, args)
                self.connection.commit()
            return True
        return False

    def updateStudentInfo(self, student, profile):
        
        if student.uid == None:
            return False

        for attr in profile:
            if not isinstance(attr[1], NotPresent):
                setattr(student, attr[0], attr[1])

        query = f"""
        UPDATE student_directory
        SET first = ?,
        last = ?,
        school = ?,
        grade = ?
        WHERE uid = ?
        """
        args = (student.first, student.last, student.school, student.grade, str(student.uid))
        self.cursor.execute(query, args)
        self.connection.commit()
        return True
    
    #
    # ACCOUNTS - GET
    #

    def getSession(self, session: Session) -> Session:
        if session.cid == None:
            return None
        
        query = f"""
        SELECT *
        FROM sessions
        WHERE cid = ?
        """
        args = (session.cid,)
        res = self.cursor.execute(query, args).fetchone()
        if res == None:
            return None
        return Session(cid=res[0], startTime=res[1], validity=res[2])

    #
    # ACCOUNTS - ADD
    #

    def addSession(self, session: Session) -> bool:
        query = f"""
        INSERT INTO sessions (
                cid, 
                start_time,
                validity
                )
            VALUES (
                ?,
                ?,
                ?
            )
        """
        args = (str(session.cid), session.startTime, session.validity)
        self.cursor.execute(query, args)
        self.connection.commit()
        return True
    
    #
    # ACCOUNTS - REMOVE
    #

    def removeSession(self, session: Session) -> bool:
        if session.id == None:
            session.id = self.getSessionID(session)
            if session.id == None:
                return False
        
        query = f"""
        UPDATE sessions
        SET validity = '{False}'
        WHERE cid = ?
        """
        args = (session.cid,)
        self.cursor.execute(query, args)
        self.connection.commit()
        return True