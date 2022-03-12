
import configparser
from fastapi import APIRouter

router = APIRouter(prefix="/teachers", tags=["Teachers"])

def adminAuth(uid: str):
    config = configparser
    config.read('config.ini')
    admin_uids = config['ADMIN']['uids']

    if uid in admin_uids:
        return True
    return False

# Query by name
# Delete absences
# Put in new absences

@router.put 