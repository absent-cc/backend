import sqlite3
from dataStructs import *
from typing import Tuple, List

# MAKE SURE TO FILTER NAMES TO PREVENT SQL INJECTION

class databaseHandler():
    classes_id = 0
    directory_id = 0

    def __init__(self, db_path="data/absent.db"):
        self.db_path = db_path
        self.reset(db_path)
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        create_directory = """
        CREATE TABLE IF NOT EXISTS directory 
        (user_id STRING PRIMARY KEY,
        number STRING, 
        first STRING,
        last STRING, 
        A_Last STRING, A_First STRING,
        B_Last STRING, B_First STRING,
        C_Last STRING, C_First STRING,
        D_Last STRING, D_First STRING,
        E_Last STRING, E_First STRING,
        F_Last STRING, F_First STRING,
        G_Last STRING, G_First STRING)
        """

        create_classes = """
        CREATE TABLE IF NOT EXISTS classes 
        (classes_id STRING PRIMARY KEY,
        teacher_first STRING,
        teacher_last STRING,
        block STRING,
        user_id STRING,
        FOREIGN KEY(user_id)
            REFERENCES directory(user_id)
                ON UPDATE CASCADE
                ON DELETE CASCADE)
        """

        self.cursor.execute(create_directory)
        self.cursor.execute(create_classes)

    def reset(self, db_path):
        import os
        if os.path.exists(db_path):
            os.remove(db_path)
            
    def __repr__(self) -> str:
        return self.print_directory() + self.print_classes()

    def newDirectoryID(self):
        databaseHandler.directory_id += 1
        return databaseHandler.directory_id

    def newClassID(self):
        databaseHandler.classes_id += 1
        return databaseHandler.classes_id
    
    def checkIfInDirectory(self, student: Student) -> bool:
        command = f"""SELECT EXISTS(SELECT 1 FROM directory WHERE number='{student.number}' LIMIT 1)
        """
        result = self.cursor.execute(command).fetchone()
        if result == (1,):
            return True
        return False
    
    def checkIfInClasses(self, teacher: Teacher) -> bool:
        command = f"""
        SELECT EXISTS(SELECT 1 FROM classes WHERE teacher_first='{teacher.first}' AND teacher_last='{teacher.last}' LIMIT 1)
        """
        result = self.cursor.execute(command).fetchone()
        if result == (1,):
            return True
        return False
    
    def teacherTupleList(self, student: Student):
        teachers: list[Tuple(str, str)]= []
        for block in student.schedule:
            teacher = student.schedule[block]
            if teacher != None:
                teachers.append((teacher.first, teacher.last))
            else:
                teachers.append(("", ""))
        return teachers
    
    def addStudentToDirectory(self, student: Student) -> bool:
        if not self.checkIfInDirectory(student):
            teachers = self.teacherTupleList(student)
            new_id = self.newDirectoryID()
        
            command = f"""
            INSERT INTO directory VALUES
            ('{new_id}', '{student.number}', '{student.first}', '{student.last}',
            '{teachers[0][0]}', '{teachers[0][1]}',
            '{teachers[1][0]}', '{teachers[1][1]}',
            '{teachers[2][0]}', '{teachers[2][1]}',
            '{teachers[3][0]}', '{teachers[3][1]}',
            '{teachers[4][0]}', '{teachers[4][1]}',
            '{teachers[5][0]}', '{teachers[5][1]}',
            '{teachers[6][0]}', '{teachers[6][1]}')
            """
            self.connection.execute(command) 
            self.connection.commit()
            return True
        return False
    
    def removeStudentFromDirectory(self, student: Student) -> bool:
        if self.checkIfInDirectory(student):
            command = f"""
            DELETE FROM directory WHERE number='{student.number}'
            """
            self.connection.execute(command)
            self.connection.commit()
            return True
        return False
    
    def updateStudentInDirectory(self, student: Student) -> bool:
        if self.checkIfInDirectory(student): 
            teachers = self.teacherTupleList(student)
            command = f"""
            UPDATE directory SET
                number='{student.number}',
                first='{student.first}',
                last='{student.last}',
                A_Last='{teachers[0][0]}', A_First='{teachers[0][1]}',
                B_Last='{teachers[1][0]}', B_First='{teachers[1][1]}',
                C_Last='{teachers[2][0]}', C_First='{teachers[2][1]}',
                D_Last='{teachers[3][0]}', D_First='{teachers[3][1]}',
                E_Last='{teachers[4][0]}', E_First='{teachers[4][1]}',
                F_Last='{teachers[5][0]}', F_First='{teachers[5][1]}',
                G_Last='{teachers[6][0]}', G_First='{teachers[6][1]}'
                WHERE number='{student.number}'
            """
            self.connection.execute(command)
            self.connection.commit()
            return True
        return False

    def getStudentFromDirectory(self, id: int = None, Number: Number = None) -> Student:
        if id != None:
            command = f"""
            SELECT * FROM directory WHERE id='{id}'
            """
            self.cursor.execute(command)
            row = self.cursor.fetchone()
            if row != None:
                teachers = []
                for teacher_names in range(4, len(row), 2):
                    teacher = Teacher(row[teacher_names], row[teacher_names+1])
                    teachers.append(teacher)
                schedule = Schedule(teachers[0], teachers[1], teachers[2], teachers[3], teachers[4], teachers[5], teachers[6])
                return Student(row[2], row[3], row[1], schedule, row[0])
        elif Number != None:
            command = f"""
            SELECT * FROM directory WHERE number='{Number}'
            """
            self.cursor.execute(command)
            row = self.cursor.fetchone()
            if row != None:
                teachers = []
                for teacher_names in range(4, len(row), 2):
                    teacher = Teacher(row[teacher_names], row[teacher_names+1])
                    teachers.append(teacher)
                schedule = Schedule(teachers[0], teachers[1], teachers[2], teachers[3], teachers[4], teachers[5], teachers[6])
                return Student(row[2], row[3], row[1], schedule, row[0])
        return None

    def addTeacherToClasses(self, teacher: Teacher, block: str, number: Number = None) -> bool:
        if number != None:
            number_to_add = str(number)
        else:
            number_to_add = ""

        if not self.checkIfInClasses(teacher):
            new_id = self.newClassID()
            command = f"""
            INSERT INTO classes VALUES
            ('{new_id}', '{teacher.first}', '{teacher.last}', '{block}', '{number_to_add}')
            """
            self.connection.execute(command)
            self.connection.commit()
            return True
        return False
    
    def updateTeacherInClasses(self, teacher: Teacher, block: str, user_id) -> bool:
        # If teacher does not exist, add them
        if not self.checkIfInClasses(teacher):
            self.addTeacherToClasses(teacher, block)
        command = f"""
        UPDATE classes SET
            first='{teacher.first}',
            last='{teacher.last}',
            block='{block}',
            number='{number}'
        WHERE first='{teacher.first}' AND last='{teacher.last} AND block='{block}'
        """
        self.connection.execute(command)
        self.connection.commit()
        return True

    # This function should never be used
    def removeTeacherFromClasses(self, teacher: Teacher, block: str) -> bool:
        if self.checkIfInClasses(teacher):
            command = f"""
            DELETE FROM classes WHERE first='{teacher.first}' AND last='{teacher.last}' AND block='{block}'
            """
            self.connection.execute(command)
            self.connection.commit()
            return True
        return False
    # def addStudentToClasses(self, student: Student) -> bool:

    def print_directory(self) -> str:
        string = ""
        self.cursor.execute("SELECT * FROM directory")
        for row in self.cursor.fetchall():
            string += str(row) + "\n"
    
    def print_classes(self) -> str:
        string = ""
        self.cursor.execute("SELECT * FROM classes")
        for row in self.cursor.fetchall(): 
            string += str(row) + "\n"
    

if __name__ == "__main__":
    NORM = Teacher("RYAN", "NORMANDIN")
    PAL = Teacher("ALEX", "PALILUNAS")
    BECKER = Teacher("RACHEL", "BECKER")
    KOZUCH = Teacher("MICAEL", "KOZUCH")
    CROSBY = Teacher("ALAN", "CROSBY")
    RUGG = Teacher("ILANA", "RUGG")

    Kevin_Schedule = Schedule(NORM, PAL, BECKER, KOZUCH, None, CROSBY, PAL)
    Kevin_Num = Number("6176868207")
    Kevin = Student("Kevin", "Yang", Kevin_Num, Kevin_Schedule)

    test = databaseHandler()
    test.addStudentToDirectory(Kevin)
    Kevin.schedule["B"] = CROSBY
    print(Kevin.schedule["B"])
    print(test.updateStudentInDirectory(Kevin))
    print(test.getStudentFromDirectory(Number="6176868207"))
    print(test.addTeacherToClasses(CROSBY, "B", Kevin_Num))
    # def add_student(self, number, first, last, a, b, c, d, e, f):
    
# connection = sqlite3.connect("data/absent.db")

# cursor = connection.cursor()

# print(connection.total_changes)