from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from api.helper import HelperFunctions
from api.accounts import Accounts
from api.routers import users, admin
from dataStructs import *
from database.databaseHandler import DatabaseHandler
from loguru import logger

# All this fucking shit for the docs because I am legitimately this vain.

description = "The abSENT API powers the mobile app you love. Here, you can interact with it and implement it into your own applications if you so desire. All documentation is open; feel free to reach out to us for help if you're unsure about how something works."
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
        "name": "Admin",
        "description": "Endpoints for administration of the service, such as sending announcements and accessing private information. Unfortunately no one but us is cool enough to have access.",
    },

]

absent = FastAPI(
    title="abSENT",
    description=description,
    version="1.0.0",
    terms_of_service="https://absent.cc/terms",
    docs_url=None, 
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
    openapi_tags=tags_metadata
)

database = DatabaseHandler()
accounts = Accounts()
helper = HelperFunctions()

# /USERS ENDPOINTS
absent.mount("/static", StaticFiles(directory="static"), name="static")
absent.include_router(users.router)
#absent.include_router(admin.router)

@absent.get("/", status_code=200, tags=["Main"])
async def serviceInfo():
    return "This is the root page of the abSENT API, v1. Please call /login to get started."

@absent.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=absent.openapi_url,
        title=absent.title + " - Documentation",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

@absent.post("/login/", status_code=201, response_model=SessionCredentials, tags=["Main"])
async def authenticate(gToken: GToken): #GOOGLE ID TOKEN WOULD BE ARG HERE.
    creds = accounts.validateGoogleToken(gToken)
    if creds != None:
        res = database.getStudentID(Student(gid=creds['sub']))
        if res != None:
            jwt = accounts.initializeSession(UUID(res))
            return SessionCredentials(token=jwt)
        else:
            id = accounts.createAccount(creds)
            if id != None:
                return SessionCredentials(token=accounts.initializeSession(id))
            else:
                helper.raiseError(500, "Account creation failed.", ErrorType.DB)

