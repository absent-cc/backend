from dataStructs import *
import sqlite3
from typing import Tuple, List
from database.logger import Logger

class DatabaseHandler():
    def __init__(self, school: SchoolName, db_path = "abSENT.db"):
        self.db_path = f"data/{db_path}"
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        create_student_directory = """
        CREATE TABLE IF NOT EXISTS student_directory (
                uuid TEXT PRIMARY KEY,
                subject TEXT,
                first_name TEXT,
                last_name TEXT,
                school TEXT,
                grade TEXT
            )
            """
        create_teacher_directory = """
        CREATE TABLE IF NOT EXISTS teacher_directory (
                teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT,
                last_name TEXT,
                school TEXT
            )
            """
        create_classes_south = """
        CREATE TABLE IF NOT EXISTS classes_south (
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
        create_classes_north = """
        CREATE TABLE IF NOT EXISTS classes_north (
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
                uuid TEXT,
                token TEXT,
                start_time TEXT,
                validity INT,
                FOREIGN KEY(uuid)
                    REFERENCES student_directory(uuid)
                    )
                """
        
        # Create tables if they don't exist
        self.cursor.execute(create_student_directory)
        self.cursor.execute(create_teacher_directory)
        self.cursor.execute(create_classes_south)
        self.cursor.execute(create_classes_north)
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
            query = f"SELECT * FROM teacher_directory WHERE first_name = '{teacher.first}' AND last_name = '{teacher.last}' LIMIT 1"
        else:
            # If teacher object already has an id, search teachers in DB by id
            query = f"SELECT * FROM teacher_directory WHERE teacher_id = '{teacher.id}' LIMIT 1"
        # Conduct query
        res = self.cursor.execute(query).fetchone()
        # If teacher is found (not None), return teacher object
        if res != None:
            teacher = Teacher(res[1], res[2], SchoolNameMapper()[res[3]], res[0])
            return teacher
        return None
    
    # Get student object from DB based off of inputted student
    def getStudent(self, student: Student):
        # Check if student object already has an id
        if student.uuid == None:
            # If not, search students in DB by student_uuid
            query = f"SELECT * FROM student_directory WHERE student_uuid = '{student.student_uuid}' LIMIT 1"
        else:
            # If student object already has an id, search students in DB by id
            query = f"SELECT * FROM student_directory WHERE student_id = '{student.uuid}' LIMIT 1"
        # Conduct query
        res = self.cursor.execute(query).fetchone()
        # If student is found (not None), return student object
        if res != None:
            student = Student(res[0], res[1], res[2], res[3], SchoolNameMapper()[res[4]], res[5])
            return student
        return None
    
    # Get teacher id from DB based off of inputted teacher
    ## Used to check if a teacher is in DB or not
    def getTeacherID(self, teacher: Teacher):
        # Check if teacher object already has an id
        if teacher.id == None:
            # If not, search teachers in DB by first + last name
            query = f"SELECT teacher_id FROM teacher_directory WHERE first_name = '{teacher.first}' AND last_name = '{teacher.last}' LIMIT 1"
            # Conduct query
            res = self.cursor.execute(query).fetchone()
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
            # If not, search students in DB by student_uuid
            query = f"SELECT student_id FROM student_directory WHERE student_uuid = '{student.student_uuid}' LIMIT 1"
            # Conduct query
            res = self.cursor.execute(query).fetchone()
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
        
        # Grab teacher id if it isn't given
        if teacher.id == None:
            teacher_id = self.getTeacherID(teacher)
        else:
            teacher_id = teacher.id
        
        # Grab student id if it isn't given
        if student.uuid == None:
            student_id = self.getStudentID(student)
        else:
            student_id = student.uuid

        query = f"SELECT class_id FROM classes WHERE teacher_id = '{teacher_id}' AND block = '{block}' AND student_id = '{student_id}' LIMIT 1"
        res = self.cursor.execute(query).fetchone()
        if res != None:
            return res[0]
        return None
        
    # Get student objects of a given grade, return as list.
    def getStudentsByGrade(self, grade: int) -> list:
        query = f"SELECT * FROM student_directory WHERE grade = '{grade}'"
        res = self.cursor.execute(query).fetchall()
        studentArray = []
        for col in res:
            # Mapping attributes from student DB to a student dataclass.
            entry = Student(col[0], col[1], col[2], col[3], SchoolNameMapper()[col[4]], col[5])
            studentArray.append(entry)
        return studentArray

    # Just grabs all students, returns list.
    def getStudents(self) -> list:
        query = f"SELECT * FROM student_directory"
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
        query = f"""
        INSERT INTO student_directory(UUID, subject, first_name, last_name, school, grade) VALUES (
            '{student.uuid}',
            '{student.subject}',
            '{student.first}',
            '{student.last}',
            '{student.school}',
            '{student.grade}'
            )
        """

        # Conduct insertion
        self.cursor.execute(query)
        query = "SELECT last_insert_rowid()"
        return_id = self.cursor.execute(query)
        student_id = return_id.fetchone()[0] # Get student id created from autoincrement
        self.connection.commit()

        updatedStudent = Student(student.uuid, student.subject, student.first, student.last, student.school, student.grade, student_id)

        self.logger.addedStudent(updatedStudent)
        # Return the newly generated id for student object manipulation
        return student_id

    # Remove student from student directory
    def removeStudentFromStudentDirectory(self, student: Student) -> bool:
        # You can only remove student if there is a student id 
        if student.uuid == None:
            return False
        # Remove student from student directory
        query = f"DELETE FROM student_directory WHERE student_id = '{student.uuid}'"
        self.cursor.execute(query)
        self.connection.commit()
        return True

    # Removes student from DB.
    def removeStudent(self, student: Student) -> bool:
        if student.uuid == None:
            return False
        # Delete a student's classes.
        query = f"DELETE FROM classes WHERE student_id = '{student.uuid}'"
        self.cursor.execute(query)
        self.connection.commit
        self.removeStudentFromStudentDirectory(student)
        return True

    # Add teacher to teacher directory
    ## Does not check whether or not teacher is already in DB, assumes not
    def addTeacherToTeacherDirectory(self, teacher: Teacher):
        # Insert teacher into teacher directory
        query = f"""
        INSERT INTO teacher_directory(
                first_name, 
                last_name, 
                school)
            VALUES (
                '{teacher.first}',
                '{teacher.last}',
                '{teacher.school}'
            )
        """
        # Conduct insertion
        self.cursor.execute(query)
        query = "SELECT last_insert_rowid()"
        return_id = self.cursor.execute(query)
        teacher_id = return_id.fetchone()[0] # Get teacher id created from autoincrement

        self.connection.commit()

        self.logger.addedTeacher(teacher)

        return teacher_id
    
    # Create a class entry for data table classes
    def addClassToClasses(self, teacher_id: int, block: SchoolBlock, student_id: int) -> Tuple[bool, int]:
        # Mapp enum SchoolBlock to string savable to DB
        str_block = BlockMapper()[block]
        # If any of the inputs are invalid, return False
        if teacher_id == None or str_block == None or student_id == None:
            return False, None
        
        query = f"""
        INSERT INTO classes(teacher_id, block, student_id) VALUES (
            '{teacher_id}',
            '{str_block}',
            '{student_id}'
            ) 
        """

        # Conduct insertion
        self.cursor.execute(query)
        query = "SELECT last_insert_rowid()"
        return_id = self.cursor.execute(query)
        class_id = return_id.fetchone()[0] # Get class id created from autoincrement

        self.connection.commit()

        return True, class_id
    
    # Building block function for class
    ## Should not be used standalone!
    def removeClassFromClasses(self, class_id: int) -> bool:
        if class_id == None:
            return False
        query = f"DELETE FROM classes WHERE class_id = '{class_id}'"
        self.cursor.execute(query)
        self.connection.commit()
        return True
    
    # Remove class from classes table
    def removeClass(self, teacher: Teacher, block: SchoolBlock, student: Student) -> bool:
        if teacher.id == None or block == None or student.uuid == None:
            return False
        class_id = self.getClassID(teacher, block, student)
        
        query = f"DELETE FROM classes WHERE class_id = '{class_id}'"
        self.cursor.execute(query)
        self.connection.commit()
        return True

    def addClass(self, student: Student, block: SchoolBlock, newTeacher: Teacher):
        # Get teacher id
        teacher_id = self.getTeacherID(newTeacher)
        if teacher_id == None:
            teacher_id = self.addTeacherToTeacherDirectory(newTeacher)
        # Get student id
        student_id = self.getStudentID(student)
        # Add class to classes table
        print(f"Created new class with id: {self.addClassToClasses(teacher_id, block, student_id)}")
        return True
    
    # Change existing class entry in data table classes
    def changeClass(self, student: Student, old_teacher: Teacher, block: SchoolBlock, new_teacher: Teacher) -> bool:
        # Map enum SchoolBlock to string savable to DB
        str_block = BlockMapper()[block]
        
        # If teacher is none type, delete specific entry for changing
        ## Note: abSENT does not store the lack of a class in the DB
        if new_teacher == None:
            if student.uuid == None:
                student.uuid = self.getStudentID(student)
            query = f"""
            DELETE FROM classes WHERE teacher_id = '{old_teacher.id}' AND block = '{str_block}' AND student_id = '{student.uuid}'
            """
            self.cursor.execute(query)
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
            FROM classes
            WHERE teacher_id = '{old_teacher.id}' AND block = '{str_block}' AND student_id = '{student.uuid}'
            """
            res = self.cursor.execute(query).fetchone()
            # If student has an empty block, we can just add this teacher to the directory.
            if res == None:
                self.addClassToClasses(new_teacher_id, block, student.uuid)
            # Else class slot full, update the class entry that already exists.
            else:
                query = f"""
                UPDATE classes 
                SET teacher_id = '{new_teacher_id}' 
                WHERE teacher_id = '{res[0]}' AND block = '{str_block}' AND student_id = '{student.uuid}'
                """
                self.cursor.execute(query)
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
            FROM classes
            WHERE teacher_id = '{teacher_id}' AND block = '{str_block}' AND school = '{str_school}'
        )
        """
        res = self.cursor.execute(query).fetchall()
        students = []
        for col in res:
            students.append(Student(col[0], col[1], col[2], col[3], col[4], col[5]))
        return students

    # Gets schedule, builds schedule object for a given student.
    def getScheduleByStudent(self, student: Student):
        schedule = Schedule()
        teachers = self.getTeachersFromStudent(student)
        # Query teacher objects for blocks and generate schedule.
        for teacher in teachers:
            query = f"""
            SELECT block
            FROM classes
            WHERE teacher_id = '{teacher.id}' AND student_id = '{student.uuid}'
            """
            res = self.cursor.execute(query).fetchall()
            for block in res:
                block = ReverseBlockMapper()[block[0]]
                if schedule[block] != None:
                    schedule[block].add(teacher)
                else:
                    schedule[block] = ClassTeachers()
                    schedule[block].add(teacher)

        return schedule
    
    def getTeachersFromStudent(self, student: Student):
        # Get raw teacher data by student.
        if student.uuid == None:
            return None
        query = f"""
        SELECT *
        FROM teacher_directory
        WHERE teacher_id in (
            SELECT teacher_id
            FROM classes
            WHERE student_id = '{student.uuid}'
        )
        """
        res = self.cursor.execute(query).fetchall()
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
        WHERE token = '{session.token}' AND uuid = '{session.uuid}'
        """
        res = self.cursor.execute(query).fetchone()
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
        WHERE session_id = '{session.id}'
        """
        res = self.cursor.execute(query).fetchone()
        if res == None:
            return None
        return Session(res[0], res[1], res[2], res[3])
    
    def addSession(self, session: Session) -> bool:
        query = f"""
        INSERT INTO sessions (
                uuid, 
                token, 
                start_time,
                validity
                )
            VALUES (
                '{session.uuid}',
                '{session.token}',
                '{session.start_time}',
                '{session.validity}'
            )
        """
        
        self.cursor.execute(query)
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
        WHERE session_id = '{session.id}'
        """
        self.cursor.execute(query)
        self.connection.commit()
        return True

    
    
    

