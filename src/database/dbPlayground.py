from . import crud

from .database import SessionLocal
from ..dataTypes import structs, schemas
from datetime import date, time, datetime

db = SessionLocal()

test = schemas.AnnouncementCreate(
    anid = "1",
    title="Test Announcement",
    content="This is a test announcement.",
    date=date.today(),
    school=structs.SchoolName.NEWTON_SOUTH
)

crud.addAnnouncement(db, test)
entry = crud.getAnnouncementByID(db, "1")
print(entry)
update = schemas.AnnouncementUpdate(
    anid="1",
    title="UPDATED",
    content="CONTENT UDPATED",
    school = structs.SchoolName.NEWTON_NORTH,
    updateTime=datetime.now()
)
crud.updateAnnouncement(db, update)
entry = crud.getAnnouncementByID(db, "1")
print(entry)

crud.removeAnnouncement(db, entry)
entry = crud.getAnnouncementByID(db, "1")