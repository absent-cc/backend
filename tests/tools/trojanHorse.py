from src.dataTypes import schemas
from src.dataTypes.structs import SchoolName
from src.database import crud
from src.database.database import SessionLocal
from src.api import accounts

# Static variables that bypass abSENT OAuth system.
# Meant for testing
class TrojanHorse:
    # Information about pseudo user
    pseudo_info = {
        "gid": "0",  # Could literaly be anything
        "first": "Trojan",
        "last": "Horse",
        "school": SchoolName.NEWTON_SOUTH,
        "grade": "10",
    }

    # Static Vars:
    _db = SessionLocal()

    husk_user = schemas.UserCreate(
        gid=int(pseudo_info["gid"]),
        first=pseudo_info["first"],
        last=pseudo_info["last"],
    )  # Create husk user to add

    user = crud.addUser(_db, husk_user)
    session = crud.addSession(_db, schemas.SessionCreate(uid=user.uid))
    token = accounts.generateToken(f"{session.sid}.{user.uid}")
    refresh = accounts.generateRefreshToken(f"{session.sid}.{user.uid}")

    creds = schemas.SessionCredentials(token=token, refresh=refresh, onboarded=False)

    counter = 0
    # For instances of Trojan Horse:
    def increment(self):
        TrojanHorse.counter += 1
        husk = {}

        husk["gid"] = str(TrojanHorse.counter)
        husk["first"] = TrojanHorse.pseudo_info["first"] + str(TrojanHorse.counter)
        husk["last"] = TrojanHorse.pseudo_info["last"] + str(TrojanHorse.counter)
        husk["school"] = TrojanHorse.pseudo_info["school"]
        husk["grade"] = TrojanHorse.pseudo_info["grade"]
        return husk

    def __init__(self):
        self.pseudo_info = TrojanHorse.increment()
        print(self.pseudo_info)
        self.husk_user = schemas.UserCreate(
            gid=int(self.pseudo_info["gid"]),
            first=self.pseudo_info["first"],
            last=self.pseudo_info["last"],
            school=TrojanHorse.husk_user.school,
            grade=TrojanHorse.husk_user.grade,
        )  # Create husk user to add

        self.trojanIn()

    def trojanIn(self):
        self.user = crud.addUser(TrojanHorse._db, self.husk_user)
        self.session = crud.addSession(
            TrojanHorse._db, schemas.SessionCreate(uid=self.user.uid)
        )
        self.token = accounts.generateToken(f"{self.session.sid}.{self.user.uid}")
        self.refresh = accounts.generateRefreshToken(
            f"{self.session.sid}.{self.user.uid}"
        )

        creds = schemas.SessionCredentials(
            token=self.token, refresh=self.refresh, onboarded=False
        )

    def resetDB(self):
        crud.reset(TrojanHorse._db)
