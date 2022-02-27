
from curses.ascii import HT
from fastapi import HTTPException
from fastapi.security.base import SecurityBase
from fastapi.openapi.models import HTTPBearer as HTTPBearerModel
from pydantic import BaseModel
from typing import Optional
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN


# Header for the API
class HTTPAuthCreds(BaseModel):
    credentials: str

class HTTPBase(SecurityBase):
    def __init__(
        self,
        *,
        bearerFormat: Optional[str] = None,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
    ):
        self.model = HTTPBearerModel(bearerFormat=bearerFormat, description=description)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthCreds]:
        authorization: str = request.headers.get("Absent-Auth")
        credentials = authorization
        if not authorization:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        return HTTPAuthCreds(credentials=credentials)




## Old code that had schemes support:

# # Header for the API
# class HTTPAuthCreds(BaseModel):
#     scheme: str
#     credentials: str

# class HTTPBase(SecurityBase):
#     def __init__(
#         self,
#         *,
#         scheme: str,
#         scheme_name: Optional[str] = None,
#         description: Optional[str] = None,
#         auto_error: bool = True,
#     ):
#         self.model = HTTPAuthCreds(scheme=scheme, description=description)
#         self.scheme_name = scheme_name or self.__class__.__name__
#         self.auto_error = auto_error

#     async def __call__(
#         self, request: Request
#     ) -> Optional[HTTPAuthCreds]:
#         authorization: str = request.headers.get("Absent-Auth")
#         scheme, credentials = get_authorization_scheme_param(authorization)
#         if not (authorization and scheme and credentials):
#             if self.auto_error:
#                 raise HTTPException(
#                     status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
#                 )
#             else:
#                 return None
#         return HTTPAuthCreds(scheme=scheme, credentials=credentials)

# class HTTPAuth(HTTPBase):
#     def __init__(
#         self,
#         *,
#         bearerFormat: Optional[str] = None,
#         scheme_name: Optional[str] = None,
#         description: Optional[str] = None,
#         auto_error: bool = True,
#     ):
#         self.model = HTTPBearerModel(bearerFormat=bearerFormat, description=description)
#         self.scheme_name = scheme_name or self.__class__.__name__
#         self.auto_error = auto_error

#     async def __call__(
#         self, request: Request
#     ) -> Optional[HTTPAuthCreds]:
#         authorization: str = request.headers.get("Absent-Auth")
#         scheme, credentials = get_authorization_scheme_param(authorization)
#         if not (authorization and scheme and credentials):
#             if self.auto_error:
#                 raise HTTPException(
#                     status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
#                 )
#             else:
#                 return None
#         if scheme.lower() != "bearer":
#             if self.auto_error:
#                 raise HTTPException(
#                     status_code=HTTP_403_FORBIDDEN,
#                     detail="Invalid authentication credentials",
#                 )
#             else:
#                 return None
#         return HTTPAuthCreds(scheme=scheme, credentials=credentials)