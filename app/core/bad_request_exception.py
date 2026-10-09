from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST


class BadRequestException(HTTPException):

    def __init__(
        self,
        detail: str,
    ):
        super().__init__(
            status_code=HTTP_400_BAD_REQUEST,
            detail=detail,
        )