# Inital execution point for pytest

from src.database import crud
from src.database.database import SessionLocal

_db = SessionLocal()

def pytest_configure(config):
    # Reset DB
    print("RESETTING DB FOR PYTEST!")
    crud.reset(_db)