from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from .routers import teachers, users, analytics, badges, admin, info
from ...api import accounts
from ...api import utils
from ...dataTypes import structs, schemas
from ...database import crud

tags_metadata = [
    {
        "name": "Main",
        "description": "Main endpoints, for logins and other queries.",
    },
    {
        "name": "Users",
        "description": "Endpoints for logged in users with credentials.",
    },
    {
        "name": "Teachers",
        "description": "Teacher related endpoints.",
    },
    {
        "name": "Analytics",
        "description": "Endpoints for analytics.",
    },
    {
        "name": "Shields.io Badges",
        "description": "Endpoints for shields.io badges",
    },
    {
        "name": "Admin",
        "description": "Endpoints for administration of the service, such as sending announcements and accessing private information.",
    },
]

description = "Point-release 2 of the abSENT API, that powers the application you love."

app = FastAPI(
    title="abSENT",
    description=description,
    terms_of_service="https://absent.cc/terms",
    version="2.0.0",
    redoc_url=None,
    contact={
        "name": "abSENT",
        "url": "https://absent.cc",
        "email": "hello@absent.cc",
    },
    license_info={
        "name": "GNU Affero General Public License v3.0",
        "url": "https://www.gnu.org/licenses/agpl-3.0.html",
    },
    openapi_tags=tags_metadata,
)


app.include_router(users.router)
app.include_router(teachers.router)
app.include_router(analytics.router)
app.include_router(badges.router)
app.include_router(admin.router)
app.include_router(info.router)


@app.get("/", status_code=200, tags=["Main"])
async def serviceInfo():
    return "This is the root page of the abSENT API, v1. Please call /login to get started."


@app.post(
    "/login/", status_code=201, response_model=schemas.SessionCredentials, tags=["Main"]
)
def authenticate(
    gToken: schemas.Token, db: Session = Depends(accounts.getDBSession)
):  # GToken is expected in request body.
    creds = accounts.validateGoogleToken(
        gToken
    )  # Accounts code is used to validate the Google JWT, returns all the data from it.
    if creds is not None:
        onboardStatus = crud.checkOnboarded(
            db, gid=creds["sub"]
        )  # Check if the user has been onboarded.
        if onboardStatus[0]:
            # User is in our table
            # Return  return the session credentials and if they have been completly onboarded.
            res = crud.getUser(db, schemas.UserReturn(gid=creds["sub"]))
            # Session is created, both tokens issued. Returned to user in body.
            session = crud.addSession(db, schemas.SessionCreate(uid=res.uid))
            token = accounts.generateToken(f"{session.sid}.{res.uid}")
            refresh = accounts.generateRefreshToken(f"{session.sid}.{res.uid}")
            return schemas.SessionCredentials(
                token=token, refresh=refresh, onboarded=onboardStatus[1]
            )

            # Remember that onboardStatus[1] is the status of whether or not they have any classes in our system. Read the checkOnboarded function for more info (database/crud.py)
        else:
            # User is not in table
            # Return session credentials and if they have been completly onboarded.
            # Account is created with the information we have from Google.
            name = creds["name"].split(" ", 1)
            if len(name) == 2:
                user = schemas.UserCreate(
                    gid=int(creds["sub"]), first=name[0], last=name[1]
                )
            else:
                user = schemas.UserCreate(gid=int(creds["sub"]), first=name[0])

            user = crud.addUser(db, user)
            # Session is created, both tokens issued. Returned to user in body.
            session = crud.addSession(db, schemas.SessionCreate(uid=user.uid))
            token = accounts.generateToken(f"{session.sid}.{user.uid}")
            refresh = accounts.generateRefreshToken(f"{session.sid}.{user.uid}")
            return schemas.SessionCredentials(
                token=token, refresh=refresh, onboarded=False
            )
            # User could not have been onboarded if they were not even in our user table.


# Endpoint used to request new main token using refresh token. Refresh token is expected in authentication header, with Bearer scheme.
@app.post(
    "/refresh/",
    status_code=201,
    response_model=schemas.SessionCredentials,
    tags=["Main"],
)
def refresh(
    cid=Depends(accounts.verifyRefreshToken),
):  # Here, the refresh token is decoded and verified using our accounts code.
    if cid is not None:  # This is the actual validity check here.
        token = accounts.generateToken(
            cid
        )  # Issue a new token, using accounts code. Since these tokens are stateless no DB interaction is needed.
        (db,) = accounts.getDBSession()
        sid, uid = cid.split(".")  # Split the cid into the session id and user id.
        inSystem, hasClasses = crud.checkOnboarded(
            db, uid=uid
        )  # Check if the user has been onboarded.
        return schemas.SessionCredentials(
            token=token, onboarded=(inSystem and hasClasses), refresh=cid
        )  # Return this using our credentials schema.
    else:
        utils.raiseError(
            401, "Invalid refresh token provided", structs.ErrorType.AUTH
        )  # Otherwise, raise an error of type AUTH, signifying an invalid token.


@app.put("/logout/", status_code=201, tags=["Main"])
def logout(
    creds: schemas.SessionReturn = Depends(accounts.verifyCredentials),
    db: Session = Depends(accounts.getDBSession),
):
    return crud.removeSession(db, creds)
