from fastapi import Request
from fastapi.responses import JSONResponse

class CustomException(Exception):
    def __init__(self, message: str):
        self.message = message

async def unicorn_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=404,
        content={"message": f"{exc.message}"},
    )
