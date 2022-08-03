from datetime import datetime, timedelta, timezone
from typing import List

from loguru import logger

from src.dataTypes import models, schemas

from .absences import AbsencePuller
from ..dataTypes import structs                 # type: ignore
from ..database import crud                     # type: ignore
from ..database.database import SessionLocal    # type: ignore
from ..notifications.notify import Notify       # type: ignore

class SchoologyListener:
    def __init__(self, SCHOOLOGYCREDS):
        self.north = structs.SchoolName.NEWTON_NORTH
        self.south = structs.SchoolName.NEWTON_SOUTH
        self.sc = AbsencePuller(SCHOOLOGYCREDS)

    # Run function, for listening and calling notifications code.
    def run(self) -> bool:
        date = datetime(2022, 6, 24)
        # date = datetime.now(timezone.utc) - timedelta( hours=5 )  # Convert from UTC --> EST

        # These statuses get updated when the listern is run.
        ## What happens is that each run function sees if the absent teachers have already been added to the database.
        ## They then update the statuses to reflect that, so in essence the state is now stored as a computed property of the absences table in the database.
        statuses = {
            # School : Tuple(pull status, notify status)
            structs.SchoolName.NEWTON_SOUTH: structs.ListenerStatus(school=self.south, date=date),  # Default is False, False (Always pull, always notify)
            structs.SchoolName.NEWTON_NORTH: structs.ListenerStatus(school=self.north, date=date),
        }

        def southRun() -> bool:
            # Get the absences
            absences = self.sc.filterAbsencesSouth(date)

            # Setup DB Session
            listenerDB = SessionLocal()

            if absences is None:
                return False

            # Add the absences to the database.
            for absence in absences:
                # Check if the absence is already in the database.
                try:
                    crud.addAbsence(listenerDB, absence)
                except Exception as e:
                    listenerDB.rollback()

            southAbsences = crud.getAbsenceList(
                listenerDB, school=structs.SchoolName.NEWTON_SOUTH, searchDate=date
            )
            listenerDB.close()
            
            southAbsencesExist: bool = (len(southAbsences) != 0)

            if southAbsencesExist:
                db = SessionLocal()
                logger.info("NSHS: Absences exist in the database")
                statuses[self.south].updateState(True, None)
                
                todays_blocks: structs.ScheduleWithTimes = crud.getSchoolDaySchedule(db, date)
                # If the absences exist, update canceled table

                southAbsences = crud.getAbsenceList(
                    db, school=structs.SchoolName.NEWTON_SOUTH, searchDate=date
                )

                for absence in southAbsences:
                    teacher: models.Teacher = absence.teacher
                    for block in todays_blocks:
                        # Classes for that specific block
                        classes: List[models.Classes]= crud.getClassesByTeacherAndBlock(db, teacher.construct_schema(), block.block)
                        if classes is None:
                             # No classes for that teacher on that block
                             # Skip to next for loop iteration
                            continue
                        for cls in classes:
                            # Check if the absence is already in the database.
                            canceled = schemas.Canceled(
                                date = date,
                                cls = cls.construct_schema(),
                            )
                            try:
                                crud.addCanceled(db, canceled)
                            except Exception as e:
                                db.rollback()
                                print(e)
                                print(f"{absence} already exists in DB")
                                return False
            
            print(crud.getCanceledsBySchool(db, structs.SchoolName.NEWTON_SOUTH, date))
            db.close()
            Notify(structs.SchoolName.NEWTON_SOUTH, date).calculateAbsencesNew()
            Notify(structs.SchoolName.NEWTON_SOUTH, date).sendMessages()
            # if (not statuses[self.south].notifications) and southAbsencesExist:
            #     logger.info("NSHS: Notifications sent")
            #     Notify(structs.SchoolName.NEWTON_SOUTH).calculateAbsencesNew()
            #     # Notify(structs.SchoolName.NEWTON_SOUTH).sendMessages()
            #     statuses[self.south].updateState(True, True)
            #     return True

            return statuses[self.south].notifications and statuses[self.south].absences

        def northRun() -> bool:
            # Get the absences
            absences = self.sc.filterAbsencesNorth(date)

            if absences is None:
                return False

            listenerDB = SessionLocal()

            # Add the absences to the database.
            for absence in absences:
                # Check if the absence is already in the database.
                try:
                    crud.addAbsence(listenerDB, absence)
                except Exception as e:
                    listenerDB.rollback()

            northAbsences = crud.getAbsenceList(
                listenerDB, school=structs.SchoolName.NEWTON_NORTH, searchDate=date
            )
            northAbsencesExist = (len(northAbsences) != 0)

            listenerDB.close()

            if northAbsencesExist:
                logger.info("NNHS: Absences exist in the database")
                statuses[self.north].updateState(True, None)
                
                db = SessionLocal()
                todays_blocks: structs.ScheduleWithTimes = crud.getSchoolDaySchedule(db, date)
                # If the absences exist, update canceled table

                southAbsences = crud.getAbsenceList(
                    db, school=structs.SchoolName.NEWTON_NORTH, searchDate=date
                )

                for absence in southAbsences:
                    teacher: models.Teacher = absence.teacher
                    for block in todays_blocks:
                        # Classes for that specific block
                        classes: List[models.Classes]= crud.getClassesByTeacherAndBlock(db, teacher.construct_schema(), block.block)
                        if classes is None:
                             # No classes for that teacher on that block
                             # Skip to next for loop iteration
                            continue
                        for cls in classes:
                            # Check if the absence is already in the database.
                            canceled = schemas.Canceled(
                                date = date,
                                cls = cls.construct_schema(),
                            )
                            try:
                                crud.addCanceled(db, canceled)
                            except Exception as e:
                                db.rollback()
                                print(e)
                                print(f"{absence} already exists in DB")
                                return False
            
            if (not statuses[self.north].notifications) and northAbsencesExist:
                logger.info("NNHS: Notifications sent")
                Notify(structs.SchoolName.NEWTON_NORTH).sendMessages()
                statuses[self.north].notifications = True
                statuses[self.north].updateState(True, True)
                return True

            return statuses[self.north].notifications and statuses[self.north].absences

        southRes = southRun()
        # northRes = northRun()

        # if southRes is None or northRes is None:
        #     logger.error("southRes or northRes is None")

        # logger.info(f"southRes: {southRes}, northRes: {northRes}")
        # return southRes and northRes
        return southRes


## Outdated
# if __name__ == "__main__":
#     config = configparser.ConfigParser()
#     config.read('config.ini')
#     creds = config['SCHOOLOGY']
#     sl = SchoologyListener(creds)
#     sl.run()
