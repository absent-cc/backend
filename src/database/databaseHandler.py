from dataStructs import *
import sqlite3
from typing import Tuple, List
from database.logger import Logger

class DatabaseHandler():
    def __init__(self, db_path = "abSENT.db"):
        self.db_path = f"data/{db_path}"
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        create_student_directory = """
        CREATE TABLE IF NOT EXISTS student_directory (
                uuid TEXT PRIMARY KEY,
                subject INT,
                first_name TEXT,
                last_name TEXT,
                school TEXT,
                grade TEXT
            )
            """
        create_teacher_directory = """
        CREATE TABLE IF NOT EXISTS teacher_directory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                school TEXT
            )
            """
        create_classes_NSHS = """
        CREATE TABLE IF NOT EXISTS classes_NSHS (
                class_id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER,
                block TEXT,
                student_uuid TEXT,
                FOREIGN KEY(student_uuid) 
                    REFERENCES student_directory(uuid)
                FOREIGN KEY(teacher_id) 
                    REFERENCES teacher_directory(teacher_id)
            )
            """
        create_classes_NNHS = """
        CREATE TABLE IF NOT EXISTS classes_NNHS (
                class_id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER,
                block TEXT,
                student_uuid TEXT,
                FOREIGN KEY(student_uuid) 
                    REFERENCES student_directory(uuid)
                FOREIGN KEY(teacher_id) 
                    REFERENCES teacher_directory(teacher_id)
            )
            """
        create_sessions = """
        CREATE TABLE IF NOT EXISTS sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_uuid TEXT,
                client_id TEXT,
                token TEXT,
                start_time TEXT,
                validity INT,
                FOREIGN KEY(student_uuid)
                    REFERENCES student_directory(uuid)
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

    # Get teacher object from DB based off of inputted teacher
    def getTeacher(self, teacher: Teacher):
        # Check if teacher object already has an id
        if teacher.id == None:
            # If not, search teachers in DB by first + last name
            query = f"SELECT * FROM teacher_directory WHERE first_name = ? AND last_name = ? LIMIT 1"
            args = (teacher.first, teacher.last)
            #query = f"SELECT * FROM teacher_directory WHERE first_name = '{teacher.first}' AND last_name = '{teacher.last}' LIMIT 1"
        else:
            # If teacher object already has an id, search teachers in DB by id
            query = f"SELECT * FROM teacher_directory WHERE id = ? LIMIT 1"
            args = (teacher.id,)
        # Conduct query
        res = self.cursor.execute(query, args).fetchone()
        # If teacher is found (not None), return teacher object
        if res != None:
            teacher = Teacher(res[1], res[2], SchoolNameMapper()[res[3]], res[0])
            return teacher
        return None
    
    # Get student object from DB based off of inputted student
    def getStudent(self, student: Student):
        # Check if student object already has an id
        if student.uuid == None:
            # If not, search students in DB by subject
            query = "SELECT * FROM student_directory WHERE subject = ? LIMIT 1"
            args = (student.subject,)
        else:
            # If student object already has an id, search students in DB by id
            query = "SELECT * FROM student_directory WHERE uuid = ? LIMIT 1"
            args = (str(student.uuid),)
        # Conduct query
        res = self.cursor.execute(query, args).fetchone()
        # If student is found (not None), return student object
        if res != None:
            if res[5] == None:
                student = Student(res[0], res[1], res[2], res[3], SchoolNameMapper()[res[4]], None)
            else:
                student = Student(res[0], res[1], res[2], res[3], SchoolNameMapper()[res[4]], res[5])
            return student
        return None
    
    # Get teacher id from DB based off of inputted teacher
    ## Used to check if a teacher is in DB or not
    def getTeacherID(self, teacher: Teacher):
        # Check if teacher object already has an id
        if teacher.id == None:
            # If not, search teachers in DB by first + last name
            query = "SELECT id FROM teacher_directory WHERE first_name = ? AND last_name = ? LIMIT 1"
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
            return teacher.id
    
    # Get student id from DB based off of inputted student
    ## Used to check if a student is in DB or not
    def getStudentID(self, student: Student):
        # Check if student object already has an id
        if student.uuid == None:
            # If not, search students in DB by uuid
            query = "SELECT uuid FROM student_directory WHERE subject = ? LIMIT 1"
            args = (student.subject,)
            # Conduct query
            res = self.cursor.execute(query, args).fetchone()
            # If student is found (not None), return student id (first in results list)
            if res != None:
                return res[0]
            else:
                return None
        else:
            # If student object already has an id, return id
            return student.uuid
    
    def getClassID(self, teacher: Teacher, block: SchoolBlock, student: Student) -> int:
        # Classes are defined by a teacher, block, and student
        
        if student.school == None:
            return None

        # Grab teacher id if it isn't given
        if teacher.id == None:
            teacher_id = self.getTeacherID(teacher)
        else:
            teacher_id = teacher.id
        
        # Grab student id if it isn't given
        if student.uuid == None:
            student_uuid = self.getStudentID(student)
        else:
            student_uuid = student.uuid

        query = f"SELECT class_id FROM classes_{ReverseSchoolNameMapper()[student.school]} WHERE teacher_id = ? AND block = ? AND student_uuid = ? LIMIT 1"
        args = (teacher_id, BlockMapper()[block], str(student_uuid))
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
            entry = Student(col[0], col[1], col[2], col[3], SchoolNameMapper()[col[4]], col[5])
            studentArray.append(entry)
        return studentArray

    # Just grabs all students, returns list.
    def getStudents(self) -> list:
        query = "SELECT * FROM student_directory"
        res = self.cursor.execute(query).fetchall()
        studentArray = []
        for col in res:
            entry = Student(col[0], col[1], col[2], col[3], SchoolNameMapper()[col[4]], col[5])
            studentArray.append(entry)
        return studentArray

    # Add student to student directory
    ## Does not check whether or not student is already in DB, assumes not
    def addStudentToStudentDirectory(self, student: Student):
        # Insert student into student directory
        query = """
        INSERT INTO student_directory(uuid, subject, first_name, last_name, school, grade) VALUES (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
            )
        """
        args = (str(student.uuid), student.subject, student.first, student.last, ReverseSchoolNameMapper()[student.school], student.grade)
        # Conduct insertion
        self.cursor.execute(query, args)
        self.connection.commit()

        updatedStudent = Student(student.uuid, student.subject, student.first, student.last, student.school, student.grade)

        self.logger.addedStudent(updatedStudent)
        # Return the newly generated id for student object manipulation
        return student.uuid

    # Remove student from student directory
    def removeStudentFromStudentDirectory(self, student: Student) -> bool:
        # You can only remove student if there is a student id 
        if student.uuid == None:
            return False
        # Remove student from student directory
        query = "DELETE FROM student_directory WHERE student_uuid = ?"
        args = (str(student.uuid),)
        self.cursor.execute(query, args)
        self.connection.commit()
        return True

    # Removes student from DB.
    def removeStudent(self, student: Student) -> bool:
        if student.uuid == None:
            return False
        if student.school == None:
            return False
        # Delete a student's classes.
        query = f"DELETE FROM classes_{ReverseSchoolNameMapper()[student.school]} WHERE student_uuid = ?"
        args = (str(student.uuid),)
        self.cursor.execute(query)
        self.connection.commit
        self.removeStudentFromStudentDirectory(student)
        return True

    # Add teacher to teacher directory
    ## Does not check whether or not teacher is already in DB, assumes not
    def addTeacherToTeacherDirectory(self, teacher: Teacher):
        # Insert teacher into teacher directory
        query = """
        INSERT INTO teacher_directory(
                first_name, 
                last_name, 
                school)
            VALUES (
                ?,
                ?,
                ?
            )
        """
        args = (teacher.first, teacher.last, SchoolNameMapper()[teacher.school])
        # Conduct insertion
        self.cursor.execute(query, args)
        query = "SELECT last_insert_rowid()"
        return_id = self.cursor.execute(query)
        teacher_id = return_id.fetchone()[0] # Get teacher id created from autoincrement

        self.connection.commit()

        self.logger.addedTeacher(teacher)

        return teacher_id
    
    # Remove class from classes table
    def removeClass(self, teacher: Teacher, block: SchoolBlock, student: Student) -> bool:
        if student.school == None:
            return False
        if teacher.id == None or block == None or student.uuid == None:
            return False
        class_id = self.getClassID(teacher, block, student)
        
        query = f"DELETE FROM classes_{ReverseSchoolNameMapper()[student.school]} WHERE class_id = ?"
        args = (class_id,)
        self.cursor.execute(query, args)
        self.connection.commit()
        return True

    def addClass(self, student: Student, block: SchoolBlock, newTeacher: Teacher):
        if student.school == None:
            return False
        # Get teacher id
        teacher_id = self.getTeacherID(newTeacher)
        if teacher_id == None:
            teacher_id = self.addTeacherToTeacherDirectory(newTeacher)
        # Get student id
        student_uuid = self.getStudentID(student)
        # Get block ENUM
        str_block = BlockMapper()[block]
        # Add class to classes table
        query = f"""
        INSERT INTO classes_{ReverseSchoolNameMapper()[student.school]}(teacher_id, block, student_uuid) VALUES (
            ?,
            ?,
            ?
            ) 
        """
        args = (teacher_id, str_block, str(student_uuid))
        self.cursor.execute(query, args)
        self.connection.commit()
        return True
    
    # Change existing class entry in data table classes
    def changeClass(self, student: Student, old_teacher: Teacher, block: SchoolBlock, new_teacher: Teacher) -> bool:
        if student.school == None:
            return None
        # Map enum SchoolBlock to string savable to DB
        str_block = BlockMapper()[block]
        
        # If teacher is none type, delete specific entry for changing
        ## Note: abSENT does not store the lack of a class in the DB
        if new_teacher == None:
            if student.uuid == None:
                student.uuid = self.getStudentID(student)
            query = f"""
            DELETE FROM classes_{ReverseSchoolNameMapper()[student.school]} WHERE teacher_id = ? AND block = ? AND student_id = ?
            """
            args = (old_teacher.id, str_block, str(student.uuid))
            self.cursor.execute(query, args)
            self.connection.commit()
            return True

        # Grab teacher id from DB
        new_teacher_id = self.getTeacherID(new_teacher)

        # If teacher id is none, then teacher does not exist
        # Add that teacher to directory
        if new_teacher_id == None:
            new_teacher_id = self.addTeacherToTeacherDirectory(new_teacher)
        
        if student.uuid != None:
            # Get teacher id for the given block and student. 
            query = f"""
            SELECT teacher_id
            FROM classes_{ReverseSchoolNameMapper()[student.school]}
            WHERE teacher_id = ? AND block = ? AND student_id = ?
            """
            args = (old_teacher.id, str_block, str(student.uuid))
            res = self.cursor.execute(query, args).fetchone()
            # If student has an empty block, we can just add this teacher to the directory.
            if res == None:
                self.addClassToClasses(new_teacher_id, block, student.uuid)
            # Else class slot full, update the class entry that already exists.
            else:
                query = f"""
                UPDATE classes_{ReverseSchoolNameMapper()[student.school]}
                SET teacher_id = ?
                WHERE teacher_id = ? AND block = ? AND student_id = ?
                """
                args = (new_teacher_id, res[0], str_block, str(student.uuid))
                self.cursor.execute(query, args)
                self.connection.commit()
            return True
        return False

    # Creates a new class entry in data table classes for student + teachers in their schedule
    ## General function to call when you want to add a user to abSENT system
    def addStudent(self, student: Student, schedule: Schedule) -> bool:
        res_student = self.getStudent(student)
        if res_student == None:
            student_uuid = self.addStudentToStudentDirectory(student)
        else:
            student_uuid = res_student.uuid
        for block in schedule:
            teachers = schedule[block]
            if teachers != None:
                for teacher in teachers:
                    # Check if teacher is already in db
                    teacher_id = self.getTeacherID(teacher)
                    if teacher_id == None:
                        teacher_id = self.addTeacherToTeacherDirectory(teacher)
                    self.addClassToClasses(teacher_id, block, student_uuid)
        return True

    def updateStudentInfo(self, student: Student, newStudent: Student) -> bool:
        if student.uuid == None:
            student.uuid = self.getStudentID(student)

        query = """
        SELECT FROM student_directory 
        """

    # Gets a list of students by absent teacher.
    def getStudentsByAbsentTeacher(self, teacher: Teacher, block: SchoolBlock, school: SchoolName) -> List[Student]:
        teacher_id = self.getTeacherID(teacher)
        if teacher_id == None:
            return []
        str_block = BlockMapper()[block]
        str_school = SchoolNameMapper()[school]

        query = f"""
        SELECT *
        FROM student_directory
        WHERE student_id IN (
            SELECT student_id
            FROM classes_{ReverseSchoolNameMapper()[teacher.school]}
            WHERE teacher_id = ? AND block = ? AND school = ?
        )
        """
        args = (teacher_id, str_block, str_school)
        res = self.cursor.execute(query, args).fetchall()
        students = []
        for col in res:
            students.append(Student(col[0], col[1], col[2], col[3], col[4], col[5]))
        return students

    # Gets schedule, builds schedule object for a given student.
    def getScheduleByStudent(self, student: Student):
        schedule = Schedule()
        teachers = self.getTeachersFromStudent(student)
        if student.school == None:
            return None
        # Query teacher objects for blocks and generate schedule.
        for teacher in teachers:
            query = f"""
            SELECT block
            FROM classes_{ReverseSchoolNameMapper()[student.school]}
            WHERE teacher_id = ? AND student_uuid = ?
            """
            args = (teacher.id, str(student.uuid))
            res = self.cursor.execute(query, args).fetchall()
            for block in res:
                block = ReverseBlockMapper()[block[0]]
                if schedule[block] != None:
                    schedule[block].add(teacher)
                else:
                    schedule[block] = ClassTeachers()
                    schedule[block].add(teacher)

        return schedule
    
    def getTeachersFromStudent(self, student: Student):
        if student.school == None:
            return None
        # Get raw teacher data by student.
        if student.uuid == None:
            return None
        query = f"""
        SELECT *
        FROM teacher_directory
        WHERE teacher_id in (
            SELECT teacher_id
            FROM classes_{ReverseSchoolNameMapper()[student.school]}
            WHERE student_uuid = ?
        )
        """
        args = (str(student.uuid),)
        res = self.cursor.execute(query, args).fetchall()
        teachers = []
        # Create teacher objects.
        for teacher in res:
            teachers.append(Teacher(teacher[1], teacher[2], SchoolNameMapper()[teacher[3]], teacher[0]))
        return teachers
    
    # Accounts stuff

    def getSessionID(self, session: Session) -> int:
        query = f"""
        SELECT session_id
        FROM sessions
        WHERE token = ? AND client_id = ?
        """
        args = (str(session.token), str(session.clientID))
        res = self.cursor.execute(query, args).fetchone()
        if res == None:
            return None
        return res[0]

    def getSession(self, session: Session) -> Session:
        if session.id == None:
            session.id = self.getSessionID(session)
            if session.id == None:
                return None
        
        query = f"""
        SELECT *
        FROM sessions
        WHERE session_id = ?
        """
        args = (session.id,)
        res = self.cursor.execute(query, args).fetchone()
        if res == None:
            return None
        return Session(res[0], res[1], res[2], res[3])
    
    def addSession(self, session: Session) -> bool:
        query = f"""
        INSERT INTO sessions (
                student_uuid,
                client_id, 
                token, 
                start_time,
                validity
                )
            VALUES (
                ?,
                ?,
                ?,
                ?,
                ?
            )
        """
        args = (str(session.studentUUID), str(session.clientID), str(session.token), session.start_time, session.validity)
        self.cursor.execute(query, args)
        self.connection.commit()
        return True
    
    def invalidateSession(self, session: Session) -> bool:
        if session.id == None:
            session.id = self.getSessionID(session)
            if session.id == None:
                return False
        
        query = f"""
        UPDATE sessions
        SET validity = '{False}'
        WHERE session_id = ?
        """
        args = (session.id,)
        self.cursor.execute(query, args)
        self.connection.commit()
        return True

    def getUUIDFromCreds(self, clientID: ClientID, token: Token):
        query = f"""
        SELECT student_uuid
        FROM sessions
        WHERE client_id = ? and token = ?
        """
        args = (str(clientID), str(token))
        res = self.cursor.execute(query, args).fetchone()
        return res[0]
    
    

