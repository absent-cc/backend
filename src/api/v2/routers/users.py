from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from ....api import accounts
from ....api import utils
from ....dataTypes import structs, schemas
from ....database import crud

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me/", response_model=schemas.UserInfoReturn, status_code=200
)  # Info endpoint.
def returnUserInfo(
    creds: schemas.SessionReturn = Depends(
        accounts.verifyCredentials
    ),  # Authentication.
    db: Session = Depends(accounts.getDBSession),  # Initializes a DB.
):
    user = schemas.UserReturn(uid=creds.uid)  # Creates husk user.
    user = crud.getUser(db, user)  # Gets the rest of the info.
    userReturn = schemas.UserReturn.from_orm(
        user
    )  # Builds a Pydantic model from this Alchemy model.
    userSettings = crud.getUserSettings(db, user)
    onboardedStatus = crud.checkOnboarded(db, uid=user.uid)

    userInfo = schemas.UserInfoReturn(
        profile=userReturn,
        schedule=schemas.ScheduleReturn.scheduleFromList(user.schedule),
        settings=userSettings,
        onboarded=onboardedStatus[0] and onboardedStatus[1],
    )  # Converts list-schedule into Schedule object.

    return userInfo  # Returns user.


@router.delete("/me/", status_code=201)  # Cancellation endpoint.
def cancel(
    creds: schemas.SessionReturn = Depends(
        accounts.verifyCredentials
    ),  # Authentication.
    db: Session = Depends(accounts.getDBSession),  # Initializes a DB.
):
    user = schemas.UserReturn(uid=creds.uid)  # Creates husk user.
    if crud.removeUser(db, user):  # Attemps remove.
        return utils.returnStatus("Account deleted.")  # Sends sucess.
    utils.raiseError(500, "Operation failed", structs.ErrorType.DB)  # Else, errors.


@router.put(
    "/me/", status_code=201, response_model=schemas.UserInfoReturn
)  # Update endpoint, main.
def updateUserInfo(
    user: schemas.UserInfoUpdate,  # Takes a user object: this is the NEW info, not the current info.
    creds: schemas.SessionReturn = Depends(
        accounts.verifyCredentials
    ),  # Authentication.
    db: Session = Depends(accounts.getDBSession),  # Initializes a DB.
):

    profile = crud.updateProfile(
        db, user.profile, creds.uid
    )  # Updates the profile info (everything save the schedule).
    schedule = crud.updateSchedule(
        db, schemas.UserReturn(uid=creds.uid, school=user.profile.school), user.schedule
    )  # Updates the schedule.
    settings = crud.updateUserSettings(db, user.settings, creds.uid)
    token = crud.updateFCMToken(db, user.fcm, creds.uid, creds.sid)

    if (profile, token, settings) is not None and schedule:
        user.schedule = schemas.ScheduleReturn().scheduleFromList(
            crud.getClassesByUser(db, schemas.UserReturn(uid=creds.uid))
        )

        return user  # Returns success.
    else:
        utils.raiseError(500, "Operation failed", structs.ErrorType.DB)


@router.put("/me/profile/", status_code=201)  # Update endpoint, profile.
def updateUserInfo(
    profile: schemas.UserBase,  # Takes just profile information.
    creds: schemas.SessionReturn = Depends(
        accounts.verifyCredentials
    ),  # Authentication.
    db: Session = Depends(accounts.getDBSession),  # Initializes a DB.
):

    result = crud.updateProfile(db, profile, creds.uid)  # Updates the profile info.

    if result is not None:
        return utils.returnStatus("Success")
    else:
        utils.raiseError(500, "Operation failed", structs.ErrorType.DB)


@router.put(
    "/me/schedule/", status_code=201, response_model=schemas.ScheduleReturn
)  # Update endpoint, schedule.
def updateUserInfo(
    schedule: schemas.Schedule,  # Takes just a schedule.
    creds: schemas.SessionReturn = Depends(
        accounts.verifyCredentials
    ),  # Authentication.
    db: Session = Depends(accounts.getDBSession),  # Initializes a DB.
):
    user = schemas.UserReturn(uid=creds.uid)  # Creates husk user.
    result = crud.updateSchedule(db, user, schedule)  # Updates schedule.

    if result:
        return schemas.ScheduleReturn().scheduleFromList(
            crud.getClassesByUser(db, user)
        )
    else:
        utils.raiseError(500, "Operation failed", structs.ErrorType.DB)


@router.put("/me/fcm/", status_code=201)
def updateFirebaseToken(
    token: schemas.Token,
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials),
    db: Session = Depends(accounts.getDBSession),
):
    result = crud.updateFCMToken(db, token, creds.uid, creds.sid)

    if result is not None:
        return utils.returnStatus("Information updated")  # Returns success.
    else:
        utils.raiseError(500, "Operation failed", structs.ErrorType.DB)


@router.put("/me/settings/", status_code=201)
def updateUserSettings(
    settings: schemas.UserSettings,
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials),
    db: Session = Depends(accounts.getDBSession),
):
    result = crud.updateUserSettings(db, settings, creds.uid)

    if result is not None:
        return utils.returnStatus("Information updated")
    else:
        utils.raiseError(500, "Operation failed", structs.ErrorType.DB)
