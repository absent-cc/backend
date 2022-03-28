from . import crud

from .database import SessionLocal
from ..dataTypes import structs

db = SessionLocal()

print(crud.getAllAbsences(db))

print(crud.getAlwaysNotify(db, structs.SchoolName.NEWTON_SOUTH))

structs.ListenerStatus.resetAll()

print(structs.SchoolName.NEWTON_NORTH.value)
status = structs.ListenerStatus(structs.SchoolName.NEWTON_SOUTH)
print(status)

status.updateState(True, True)

print(status.readState())
