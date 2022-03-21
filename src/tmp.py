from .api import accounts
from .database import crud
from .database.database import SessionLocal
from datetime import datetime

date = datetime.now().date()
db = SessionLocal()
crud.removeDayAbsences(db, date)
