import json
from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session
from src.api import accounts
from src.dataTypes import schemas
from src.database import crud

class UserProfilePopulate:
    def __init__(self) -> None:
        self.db: Session = accounts.getDBSession().__next__()
        self.data = self.loadData()
        self.populateDB()

    def loadData(self) -> List[schemas.UserInfoReturn]:
        with open("tests/unit/data/full_user_profiles.json", "r") as f:
            raw_data = json.load(f)
            data: List[schemas.UserInfoReturn] = []

            return [schemas.UserInfoReturn(**user) for user in raw_data]
    
    def populateDB(self) -> None:
        for user in self.data:
            print(user)
            userEntry = crud.addUser(self.db, schemas.UserCreate(**user.profile.__dict__))
            # print(type(userEntry))
            print(userEntry)
            userObject = schemas.UserReturn(**userEntry.__dict__)
            crud.updateSchedule(self.db, userObject, schemas.Schedule(**user.schedule.__dict__))
            crud.updateUserSettings(self.db, schemas.UserSettings(**user.settings.__dict__), uid=userObject.uid)

            print(crud.getUsersByName(self.db, user.profile.first, user.profile.last)) # type: ignore

UserProfilePopulate()
