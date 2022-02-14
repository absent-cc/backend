import csv
from typing import List
import unittest

from sqlalchemy import delete
from src.database import crud
from src.database.database import SessionLocal
from src.dataTypes import models
from src.dataTypes.schemas import UserBase, UserCreate, UserReturn
from src.dataTypes.structs import SchoolNameMapper

example_users_path = "tests/unit/database/data/test_users.csv"

# Helper function that will load example users from csv 
# and convert them in userbase obejcts
def load_example_users() -> List[UserBase]:
    pseduo_gid = 0

    example_users: List[UserCreate] = []
    with open(example_users_path, "r") as f:
        file = csv.reader(f)
        for row in file:
            stripped_row = [x.strip() for x in row]
            user = UserCreate(
                first=stripped_row[0],
                last=stripped_row[1],
                school= SchoolNameMapper()[stripped_row[2]],
                grade = int(stripped_row[3]),
                gid = str(pseduo_gid)
            )
            example_users.append(user)
            pseduo_gid += 1
    return example_users

# CRUD Testing for adding users
class AddUsers(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName='runTest')
        self.db = SessionLocal()
        self.users = []

    def reset_db(self):
        query = delete(models.User)
        self.db.execute(query) 
        self.db.commit()

    def runTest(self):
        self.reset_db() # Reset DB
        self.add_example_users() # Add users
        self.check_amount_added() # Check if users were added

        example_users = load_example_users()
        self.compare_added_users(example_users) # Compare added users with example users

    # Add example users to db
    def add_example_users(self):
        example_users = load_example_users()
        for user in example_users:
            # Add users to db
            crud.addUser(self.db, user) 

    # Check if users were added
    def check_amount_added(self):
        self.assertEqual(len(self.db.query(models.User).all()), len(load_example_users())), "Failed to add users"

    # Compare added users with example users 
    def compare_added_users(self, example_users):
        for user in example_users:
            db_user = self.db.query(models.User).filter(models.User.first == user.first, models.User.last == user.last, models.User.school == user.school).first()
            self.assertEqual(db_user.first, user.first)
            self.assertEqual(db_user.last, user.last)
            self.assertEqual(db_user.school, user.school)
            self.assertEqual(db_user.grade, user.grade)
            self.assertEqual(db_user.gid, user.gid)

class GetUsers(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.db = SessionLocal()
    
    def reset_db(self):
        query = delete(models.User)
        self.db.execute(query) 
        self.db.commit()
    
    def runTest(self):
        self.reset_db()
        self.add_example_users()
        self.check_users_with_get()

    def add_example_users(self):
        AddUsers().add_example_users()

    def check_users_with_get(self):
        example_users = crud.getAllUsers(self.db)
        for user in example_users:
            return_user = UserReturn(
                first=user.first,
                last=user.last,
                school=user.school,
                grade=user.grade,
                gid=user.gid,
                uid=user.uid
            )

            db_user = crud.getUser(self.db, return_user)
            self.assertEqual(db_user.first, user.first)
            self.assertEqual(db_user.last, user.last)
            self.assertEqual(db_user.school, user.school)
            self.assertEqual(db_user.grade, user.grade)
            self.assertEqual(db_user.gid, user.gid)
    

class DeleteUsers(unittest.TestCase):
    def __init__(self, methodName = "runTest"):
        super().__init__(methodName="runTest")
        self.db = SessionLocal()
        self.addUser = AddUsers()
    
    def reset_db(self):
        query = delete(models.User)
        self.db.execute(query)
        self.db.commit()
    
    def runTest(self):
        self.reset_db()
        addCrud = AddUsers()
        addCrud.add_example_users() # Add in example users
        self.delete_example_users()
    
    def delete_example_users(self):
        pass # FIX LATER
        # example_users = load_example_users()
        # for user in example_users:
            # crud.removeUser(self.db, user)
        # self.assertEqual(len(self.db.query(models.User).all()), 0), "Failed to delete all users"
    
        # def delete_example_users():
        #     example_users = load_example_users()
        #     for user in example_users:
        #         crud.addUser(self.db, user)
        #     return example_users

    

if __name__ == "__main__":
    unittest.main()
