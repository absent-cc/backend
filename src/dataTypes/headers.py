
from fastapi import HTTPException
from fastapi.security.http import HTTPBase
from fastapi.openapi.models import HTTPBearer as HTTPBearerModel
from pydantic import BaseModel, validator
from typing import Optional
from starlette.requests import Request
from fastapi.security.utils import get_authorization_scheme_param
from starlette.status import HTTP_403_FORBIDDEN

# Header for the API
class HTTPAuthCreds(BaseModel):
    scheme: str
    credentials: str

    # Basic checking for the creds
    # @validator('credentials')
    # def checkCredentials(cls, v):
    #     if len(v) != 64:
    #         raise ValueError('Invalid Credentials from validator.')
    #     return v

class HTTPAuth(HTTPBase):
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
        authorization: str = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None
        if scheme.lower() != "absent-auth":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Invalid authentication credentials",
                )
            else:
                return None
        return HTTPAuthCreds(scheme=scheme, credentials=credentials)

