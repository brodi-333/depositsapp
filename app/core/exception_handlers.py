from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError


async def value_and_assertion_error_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    for error in exc.errors():
        if "msg" not in error:
            continue

        if error['msg'].startswith("Value error, "):
            error['msg'] = error['msg'].removeprefix("Value error, ")
        if error['msg'].startswith("Assertion failed, "):
            error['msg'] = error['msg'].removeprefix("Assertion failed, ")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(exc.errors())},
    )


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(RequestValidationError, value_and_assertion_error_exception_handler)
