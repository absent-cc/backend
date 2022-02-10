from src.database.database import SessionLocal
from src.database import crud
from src.dataTypes import schemas
from src.api import accounts

import os

# Static variables that bypass abSENT OAuth system.
# Meant for testing
class TrojanHorse():
    # Information about pseudo user
    pseudo_info = {
        "gid": "12345", # Could literaly be anything
        "first": "Trojan",
        "last": "Horse",
    }

    husk_user = schemas.UserCreate(gid=int(pseudo_info["gid"]), first=pseudo_info["first"], last=pseudo_info["last"]) # Create husk user to add

    _db = SessionLocal()

    if os.environ.get("TrojanHorse") == None or os.environ.get("TrojanHorse") == "False": # Latching system so we don't reset the database every time we call TrojansHorse
        crud.reset(_db)
        print("RESETTING DATABASE TROJAN HORSE")
        user = crud.addUser(_db, husk_user)
        session = crud.addSession(_db, schemas.SessionCreate(uid=user.uid))
        token = accounts.generateToken(f"{session.sid}.{user.uid}")
        refresh = accounts.generateRefreshToken(f"{session.sid}.{user.uid}")
        
        creds = schemas.SessionCredentials(token=token, refresh=refresh, onboarded=False)
        os.environ["TrojanHorse"] = 'True'

    # completed = False

    # if not completed:
    #     crud.reset(db)
    #     print("Resetting database")
    #     user = crud.addUser(db, husk_user)
    #     session = crud.addSession(db, schemas.SessionCreate(uid=user.uid))
    #     token = accounts.generateToken(f"{session.sid}.{user.uid}")
    #     refresh = accounts.generateRefreshToken(f"{session.sid}.{user.uid}")
        
    #     creds = schemas.SessionCredentials(token=token, refresh=refresh, onboarded=False)
    #     os.environ["TrojanHorse"] = 'True'
    #     completed = True