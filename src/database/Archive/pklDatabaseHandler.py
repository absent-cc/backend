from dataStructs import *
import pickle
import os

from typing import Tuple

class DatabaseHandler:
    # abSENT's database consists of two structures:
    # 1. Classes: a dictionary that maps a teacher to a set of students
    # 2. Directory: a dictionary that maps a unique number its coorsponding student

    # Classes is used to notify each student when a teacher is absent
    # Directory is meant to keep track of who is part of the abSENT system (think of user directory)

    # Type definitions:
    classes: Classes
    directory: Directory

    # Note: For classes, teacher maps to a set of students in order to ensure uniquness and no repeats, rather than a non-unique list.

    def __init__(self, directory_path: str ='data/directory.pkl', classes_path: str ='data/classes.pkl'):
        self.directory_path = directory_path
        self.directory = self.readDirectory(directory_path)
        self.classes = self.readClasses(classes_path)
    
    # Read objects from pickle file
    def readPickle(self, path):
        if path.lower().endswith(('.pkl')): # Check if path points to a pickle file
            if not os.stat(path).st_size == 0: # Check if pickle file is empty
                with open(path, 'rb') as f: 
                    return pickle.load(f) # Load pickle file
            else:
                return None # There is no file, so return an empty dictionary
        else:
            raise Exception('Directory Path is not a pickle file')

    def readDirectory(self, path: str ='data/directory.pkl') -> Directory:
        res = self.readPickle(path)
        if res == None:
            return Directory()
        return res
    
    def readClasses(self, path: str = 'data/classes.pkl') -> Classes:
        res = self.readPickle(path)
        if res == None:
            return Classes()
        return res

    # Write objects to a pickle file
    def writeToPickle(self, object, path) -> bool:
        with open(path, 'wb') as f:
            pickle.dump(object, f)
            return True # Object sucessfully written to {path}.pkl
    
    # Save current instance of directory to pickle file
    def saveDirectory(self, directory, path='data/directory.pkl') -> bool:
        return self.writeToPickle(directory, path)

    # Save current instance of classes to pickle file
    def saveClasses(self, classes, path='data/classes.pkl') -> bool:
        return self.writeToPickle(classes, path)
        
    # Add student to user directory
    def addStudentToDirectory(self, student: Student) -> bool:
        # Check if student is already in directory
        if student.number not in self.directory:
            self.directory[student.number] = student # Create new number, student pair in directory
            self.saveDirectory(self.directory) # Save changes
            return True # Student sucessfully added to directory
        return False # Student already exists in directory

    # Remove student from directory 
    def removeStudentFromDirectory(self, student: Student) -> bool:
        # Check if student is in directory
        if student.number in self.directory:
            del self.directory[student.number] # Delete number key from directory dictionary
            self.saveDirectory(self.directory) # Save changes
            return True # Student sucessfully removed from directory
        return False # Student does not exist in directory
    
    # Add teacher to classes
    def addTeacher(self, teacher: Teacher) -> bool:
        # Check if teacher is already in classes
        if teacher not in self.classes:
            self.classes[teacher] = set() # Create a new key, value pair for teacher. Set its class to empty
            self.saveClasses(self.classes) # Save changes
            return True # Teacher sucessfully added to classes
        return False # Teacher already exists in classes
    
    # Remove teacher from classes
    def removeTeacher(self, teacher: Teacher) -> bool:
        if teacher in self.classes:
            del self.classes[teacher] # Delete teacher entry from classes
            self.saveClasses(self.classes) # Save changes
            return True
        return False # Teacher not in classses, cannot remove student
    
    # Add student to its respective teachers' classes
    def addStudentToClass(self, student: Student, teacher: Teacher) -> bool:
        if teacher in self.classes:
            self.classes[teacher].add(student) # Add student to teacher's class
            self.saveClasses(self.classes) # Save Changes
            return True # Student sucessfully added to class
        return False
    
    # Remove student from its respective teachers' classes
    def removeStudentFromClass(self, student: Student, teacher: Teacher) -> bool:
        if teacher in self.classes:
            self.classes[teacher].remove(student)
            self.saveClasses(self.classes)
            # If a teacher's class becomes empty, delete the teacher
            if len(self.classes[teacher]) == 0:
                self.removeTeacher(teacher)
            return True # Student sucessfully removed from class
        return False # Teacher not in classes, cannot remove student

    def addStudent(self, student: Student) -> Tuple[bool,str]:
        # Add student to directory
        res = self.addStudentToDirectory(student)
        # If student sucessfully added to directory,
        # add student to all of its classes
        if res == True:
            trace = ""
            for block in student.schedule:
                teacher = student.schedule[block]
                # Add student to teacher's class
                res = self.addStudentToClass(student, teacher)
                # If false, add teacher into classes
                if res == False:
                    trace += f"Added {teacher} to classes\n" # Produce a trace for logging
                    self.addTeacher(teacher)
                    self.addStudentToClass(student, teacher)
            return (True, trace)
        return False, "Student already exists"
    
    def removeStudent(self, student: Student) -> Tuple[bool,str]:
        # Remove student from directory
        res = self.removeStudentFromDirectory(student)
        # If student sucessfully removed from directory,
        # remove student from all of its classes
        if res == True:
            trace = ""
            for teacher in student.schedule:
                # Remove student from teacher's class
                res = self.removeStudentFromClass(student, teacher)
                # If false, do nothing and record the trace
                if res == False:
                    trace += f"Student or Teacher not in system"
            return (True, trace)
        return False, "Student does not exist"

    def changeClass(self, student: Student, block: str, new_teacher: Teacher) -> Tuple[bool,str]:
        # Check if block is valid
        if block in student.schedule:
            # Grab old_teacher name through mapper dictionary | Block -> Teacher
            old_teacher = student.schedule[block]
        else:
            return False, "Block does not exist"
        # Remove student from old teacher's class
        res_remove = self.removeStudentFromClass(student, old_teacher)
        # If student sucessfully removed from old teacher's class,
        # add student to new teacher's class
        if res_remove == True:
            res_add = self.addStudentToClass(student, new_teacher)
            student.schedule[block] = new_teacher
            # If student sucessfully added to new teacher's class,
            # return true and empty trace
            if res_add == True:
                return (True, "")
            # If student not added to new teacher's class,
            # add new teacher to classes
            else:
                self.addTeacher(new_teacher)
                self.addStudentToClass(student, new_teacher)
                return (True, "")
        # If student not removed from old teacher's class,
        # return false and empty trace
        return (False, "Teacher not in classes")
    
    # Grab student info from directory
    def getStudent(self, number: Number) -> Student:
        # Check if student is in directory
        if number in self.directory:
            return self.directory[number]
    
    def reset(self):
        self.directory = Directory()
        self.classes = Classes()
        self.saveDirectory(self.directory)
        self.saveClasses(self.classes)
