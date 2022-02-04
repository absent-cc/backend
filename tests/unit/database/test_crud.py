import unittest
from src.dataTypes.schemas import UserBase, UserCreate
from src.dataTypes.structs import SchoolNameMapper
from src.dataTypes import models
from src.database.database import SessionLocal
from src.database import crud
import csv

from sqlalchemy import delete

example_users_path = "tests/unit/database/data/test_users.csv"

# Helper function that will load example users from csv 
# and convert them in userbase obejcts
def load_example_users() -> list[UserBase]:
    pseduo_gid = 0

    example_users: list[UserCreate] = []
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

class AddUsers(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName='runTest')
        self.db = SessionLocal()

    def reset_db(self):
        query = delete(models.User)
        self.db.execute(query) 
        self.db.commit()

    def runTest(self):
        self.reset_db() # Reset DB
        self.test_add_user()
    
    def add_user(self):
        def add_example_users():
            example_users = load_example_users()
            for user in example_users:
                crud.addUser(self.db, user)
            return example_users
        
        def check_amount_added(self):
            self.assertEqual(len(self.db.query(models.User).all()), len(load_example_users())), "Failed to add users"
        
        def compare_added_users(self, example_users):
            for user in example_users:
                db_user = self.db.query(models.User).filter(models.User.first == user.first, models.User.last == user.last, models.User.school == user.school).first()
                self.assertEqual(db_user.first, user.first)
                self.assertEqual(db_user.last, user.last)
                self.assertEqual(db_user.school, user.school)
                self.assertEqual(db_user.grade, user.grade)
                self.assertEqual(db_user.gid, user.gid)
        
        example_users = load_example_users()
        add_example_users()
        check_amount_added(self)
        compare_added_users(self, example_users)

if __name__ == "__main__":
    unittest.main()