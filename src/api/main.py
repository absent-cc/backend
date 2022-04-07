import time

from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from .v1 import main as v1

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
    # {
    #     "name": "Admin",
    #     "description": "Endpoints for administration of the service, such as sending announcements and accessing private information. Unfortunately no one but us is cool enough to have access.",
    # },
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


def init_app():
    # Initalize the API
    absent = FastAPI(
        title="abSENT",
        description=description,
        version="1.1.0",
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
        openapi_tags=tags_metadata,
    )

    @absent.middleware("http")
    async def addCorsHeader(request: Request, call_next):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    @absent.middleware("http")
    async def addProcessTime(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response

    absent.mount("/static", StaticFiles(directory="static"), name="static")

    @absent.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=absent.openapi_url,
            title=absent.title + " - Documentation",
            swagger_js_url="/static/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui.css",
        )

    absent.include_router(v1.router)  # Include routers for V1 API

    return absent


if __name__ == "__main__":
    absentApp = init_app()
