from datetime import datetime, timedelta, timezone

from loguru import logger

from .absences import AbsencePuller
from ..dataTypes import structs
from ..database import crud
from ..database.database import SessionLocal
from ..notifications.notify import Notify


class SchoologyListener:
    def __init__(self, SCHOOLOGYCREDS):
        self.north = structs.SchoolName.NEWTON_NORTH
        self.south = structs.SchoolName.NEWTON_SOUTH
        self.restTime = timedelta(seconds=30)
        self.sc = AbsencePuller(SCHOOLOGYCREDS)

    # Run function, for listening and calling notifications code.
    
    def currentTime(self) -> datetime:
        return datetime.now(timezone.utc) - timedelta(hours=5)
    
        # These statuses get updated when the listern is run.
        ## What happens is that each run function sees if the absent teachers have already been added to the database.
        ## They then update the statuses to reflect that, so in essence the state is now stored as a computed property of the absences table in the database.

    def southRun(self) -> bool:
        date = self.currentTime()

        status: structs.ListenerStatus = structs.ListenerStatus(school=self.south)

        # Get the absences
        absences = self.sc.filterAbsences(structs.SchoolName.NEWTON_SOUTH, date)

        # Setup DB Session
        listenerDB = SessionLocal()

        if absences is None:
            return False

        # Add the absences to the database.
        for absence in absences:
            # Do not add the absence if it is a on our "black list":
            if (
                (absence.teacher.first is None) or 
                (absence.teacher.last is None) or 

                (absence.teacher.first == "") or 
                (absence.teacher.last == "") or

                (absence.teacher.first.lower() == "first") or
                (absence.teacher.last.lower() == "last") or
                (absence.teacher.first.lower() == "last name") or
                (absence.teacher.last.lower() == "last name")
                ):
                continue
            
            # Check if the absence is already in the database.
            try:
                crud.addAbsence(listenerDB, absence)
            except Exception as e:
                listenerDB.rollback()

        southAbsences = crud.getAbsenceList(
            listenerDB, school=structs.SchoolName.NEWTON_SOUTH
        )
        southAbsencesExist = len(southAbsences) != 0

        listenerDB.close()

        if southAbsencesExist:
            logger.info("NSHS: Absences exist in the database")
            status.updateState(True, None)

        if (not status.notifications) and southAbsencesExist:
            logger.info("NSHS: Notifications sent")
            Notify(structs.SchoolName.NEWTON_SOUTH).sendMessages()
            status.updateState(True, True)
            return True

        # Return whether you will need to run south again.
        return status.notifications and status.absences

    def northRun(self) -> bool:
        date = self.currentTime()
        status: structs.ListenerStatus = structs.ListenerStatus(school=self.north)
        # Get the absences
        absences = self.sc.filterAbsences(structs.SchoolName.NEWTON_NORTH, date)

        if absences is None:
            return False

        listenerDB = SessionLocal()

        # Add the absences to the database.
        for absence in absences:
            if (
                (absence.teacher.first is None) or 
                (absence.teacher.last is None) or 

                (absence.teacher.first == "") or 
                (absence.teacher.last == "") or

                (absence.teacher.first.lower() == "first") or
                (absence.teacher.last.lower() == "last") or
                (absence.teacher.first.lower() == "last name") or
                (absence.teacher.last.lower() == "last name")
                ):
                continue
            # Check if the absence is already in the database.
            try:
                crud.addAbsence(listenerDB, absence)
            except Exception as e:
                listenerDB.rollback()

        northAbsences = crud.getAbsenceList(
            listenerDB, school=structs.SchoolName.NEWTON_NORTH
        )
        northAbsencesExist = len(northAbsences) != 0

        listenerDB.close()

        if northAbsencesExist:
            logger.info("NNHS: Absences exist in the database")
            status.updateState(True, None)

        if (not status.notifications) and northAbsencesExist:
            logger.info("NNHS: Notifications sent")
            Notify(structs.SchoolName.NEWTON_NORTH).sendMessages()
            status.notifications = True
            status.updateState(True, True)
            return True

        return status.notifications and status.absences


# if __name__ == "__main__":
#     config = ConfigParser()
#     config.read('config.ini')
#     creds = config['SCHOOLOGY']
#     sl = SchoologyListener(creds)
#     sl.run()
