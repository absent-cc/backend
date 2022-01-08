from dataStructs import *
import sqlite3
from typing import Tuple, List
from database.logger import Logger

class DatabaseHandler():
    def __init__(self, school: SchoolName, db_path = "abSENT.db"):
        self.db_path = f"data/{school.name}_{db_path}"
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        create_student_directory = """
        CREATE TABLE IF NOT EXISTS student_directory (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject INT,
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
        create_classes = """
        CREATE TABLE IF NOT EXISTS classes (
                class_id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER,
                block TEXT,
                student_id INTEGER,
                FOREIGN KEY(student_id) 
                    REFERENCES student_directory(student_id)
                FOREIGN KEY(teacher_id) 
                    REFERENCES teacher_directory(teacher_id)
            )
            """
        
        # Create tables if they don't exist
        self.cursor.execute(create_student_directory)
        self.cursor.execute(create_teacher_directory)
        self.cursor.execute(create_classes)

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
        if student.id == None:
            # If not, search students in DB by number
            query = f"SELECT * FROM student_directory WHERE number = '{student.number}' LIMIT 1"
        else:
            # If student object already has an id, search students in DB by id
            query = f"SELECT * FROM student_directory WHERE student_id = '{student.id}' LIMIT 1"
        # Conduct query
        res = self.cursor.execute(query).fetchone()
        # If student is found (not None), return student object
        if res != None:
            student = Student(res[1], res[2], res[3], SchoolNameMapper()[res[4]], res[5], res[0])
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
        if student.id == None:
            # If not, search students in DB by number
            query = f"SELECT student_id FROM student_directory WHERE number = '{student.number}' LIMIT 1"
            # Conduct query
            res = self.cursor.execute(query).fetchone()
            # If student is found (not None), return student id (first in results list)
            if res != None:
                return res[0]
            else:
                return None
        else:
            # If student object already has an id, return id
            return student.id
    
    def getClassID(self, teacher: Teacher, block: SchoolBlock, student: Student) -> int:
        # Classes are defined by a teacher, block, and student
        
        # Grab teacher id if it isn't given
        if teacher.id == None:
            teacher_id = self.getTeacherID(teacher)
        else:
            teacher_id = teacher.id
        
        # Grab student id if it isn't given
        if student.id == None:
            student_id = self.getStudentID(student)
        else:
            student_id = student.id

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
        for student in res:
            # Mapping attributes from student DB to a student dataclass.
            entry = Student(student[1], student[2], student[3], student[4], student[5], student[0])
            studentArray.append(entry)
        return studentArray

    # Just grabs all students, returns list.
    def getStudents(self) -> list:
        query = f"SELECT * FROM student_directory"
        res = self.cursor.execute(query).fetchall()
        studentArray = []
        for student in res:
            entry = Student(student[1], student[2], student[3], student[4], student[5], student[0])
            studentArray.append(entry)
        return studentArray

    # Add student to student directory
    ## Does not check whether or not student is already in DB, assumes not
    def addStudentToStudentDirectory(self, student: Student):
        # Insert student into student directory
        query = f"""
        INSERT INTO student_directory(number, first_name, last_name, school, grade) VALUES (
            '{student.number}',
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

        updatedStudent = Student(student.number, student.first, student.last, student.school, student.grade, student_id)

        self.logger.addedStudent(updatedStudent)
        # Return the newly generated id for student object manipulation
        return student_id

    # Removes student from DB.
    def removeStudent(self, student: Student) -> bool:
        if student.id == None:
            return False
        # Delete a student's classes.
        query = f"DELETE FROM classes WHERE student_id = '{student.id}'"
        self.cursor.execute(query)
        self.connection.commit
        self.removeStudentFromStudentDirectory(student)
        return True

    # Remove student from student directory
    def removeStudentFromStudentDirectory(self, student: Student) -> bool:
        # You can only remove student if there is a student id 
        if student.id == None:
            return False
        # Remove student from student directory
        query = f"DELETE FROM student_directory WHERE student_id = '{student.id}'"
        self.cursor.execute(query)
        self.connection.commit()
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
        if teacher.id == None or block == None or student.id == None:
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
            if student.id == None:
                student.id = self.getStudentID(student)
            query = f"""
            DELETE FROM classes WHERE teacher_id = '{old_teacher.id}' AND block = '{str_block}' AND student_id = '{student.id}'
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
        
        if student.id != None:
            # Get teacher id for the given block and student. 
            query = f"""
            SELECT teacher_id
            FROM classes
            WHERE teacher_id = '{old_teacher.id}' AND block = '{str_block}' AND student_id = '{student.id}'
            """
            res = self.cursor.execute(query).fetchone()
            # If student has an empty block, we can just add this teacher to the directory.
            if res == None:
                self.addClassToClasses(new_teacher_id, block, student.id)
            # Else class slot full, update the class entry that already exists.
            else:
                query = f"""
                UPDATE classes 
                SET teacher_id = '{new_teacher_id}' 
                WHERE teacher_id = '{res[0]}' AND block = '{str_block}' AND student_id = '{student.id}'
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
            student_id = self.addStudentToStudentDirectory(student)
        else:
            student_id = res_student.id
        for block in schedule:
            teachers = schedule[block]
            if teachers != None:
                for teacher in teachers:
                    # Check if teacher is already in db
                    teacher_id = self.getTeacherID(teacher)
                    if teacher_id == None:
                        teacher_id = self.addTeacherToTeacherDirectory(teacher)
                    self.addClassToClasses(teacher_id, block, student_id)
        return True

    # Gets a list of students by absent teacher.
    def queryStudentsByAbsentTeacher(self, teacher: Teacher, block: SchoolBlock) -> List[Student]:
        teacher_id = self.getTeacherID(teacher)
        if teacher_id == None:
            return []
        str_block = BlockMapper()[block]
        query = f"""
        SELECT *
        FROM student_directory
        WHERE student_id IN (
            SELECT student_id
            FROM classes
            WHERE teacher_id = '{teacher_id}' AND block = '{str_block}'
        )
        """
        res = self.cursor.execute(query).fetchall()
        students = []
        for col in res:
            students.append(Student(col[1], col[2], col[3], col[4], col[5], col[0]))
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
            WHERE teacher_id = '{teacher.id}' AND student_id = '{student.id}'
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
        if student.id == None:
            return None
        query = f"""
        SELECT *
        FROM teacher_directory
        WHERE teacher_id in (
            SELECT teacher_id
            FROM classes
            WHERE student_id = '{student.id}'
        )
        """
        res = self.cursor.execute(query).fetchall()
        teachers = []
        # Create teacher objects.
        for teacher in res:
            teachers.append(Teacher(teacher[1], teacher[2], SchoolNameMapper()[teacher[3]], teacher[0]))
        return teachers