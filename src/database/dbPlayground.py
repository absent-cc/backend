from . import crud

from .database import SessionLocal
from ..dataTypes import structs

db = SessionLocal()

print(crud.getAllAbsences(db))

print(crud.getAlwaysNotify(db, structs.SchoolName.NEWTON_SOUTH))

