from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.controllers.base_controller import BaseController
from app.core.config import settings
from app.core.logger import logger
from app.utils.validation_errors import format_request_validation_errors
from app.exceptions import (
    AppException,
    BadRequestError,
    ForbiddenError,
    UnauthorizedError,
)

app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exc: StarletteHTTPException):
    if exc.status_code >= 500:
        logger.exception("HTTP exception %s: %s", exc.status_code, exc.detail)
    detail = exc.detail
    if not isinstance(detail, str):
        detail = str(detail)
    code = exc.status_code
    if code == 401:
        return BaseController.respond_unauthorized(detail)
    if code == 403:
        return BaseController.respond_forbidden(detail)
    if code == 404:
        return BaseController.respond_not_found(detail)
    if code == 422:
        return BaseController.respond_validation_error(detail)
    if code >= 500:
        return BaseController.respond_internal_error(detail)
    return BaseController.respond_bad_request(detail)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    logger.warning("Request validation error: %s", exc.errors())
    structured = format_request_validation_errors(exc.errors())
    return BaseController.respond_validation_error("Validation error", structured)


@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(_: Request, exc: UnauthorizedError):
    return BaseController.respond_unauthorized(exc.message, exc.errors)


@app.exception_handler(ForbiddenError)
async def forbidden_handler(_: Request, exc: ForbiddenError):
    return BaseController.respond_forbidden(exc.message, exc.errors)


@app.exception_handler(BadRequestError)
async def bad_request_handler(_: Request, exc: BadRequestError):
    return BaseController.respond_bad_request(exc.message, exc.errors)


@app.exception_handler(AppException)
async def app_exception_handler(_: Request, exc: AppException):
    if exc.status_code == 401:
        return BaseController.respond_unauthorized(exc.message, exc.errors)
    if exc.status_code == 403:
        return BaseController.respond_forbidden(exc.message, exc.errors)
    if exc.status_code == 404:
        return BaseController.respond_not_found(exc.message, exc.errors)
    if exc.status_code == 409:
        return BaseController.respond_conflict(exc.message, exc.errors)
    if exc.status_code == 422:
        return BaseController.respond_validation_error(exc.message, exc.errors)
    if exc.status_code >= 500:
        return BaseController.respond_internal_error(exc.message, exc.errors)
    return BaseController.respond_bad_request(exc.message, exc.errors)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    logger.exception("Unhandled server exception: %s", exc)
    return BaseController.respond_internal_error("Unexpected server error")


@app.get("/health")
async def health():
    return BaseController.respond_success({"status": "ok"}, "Service healthy")


@app.get("/root")
async def root():
    return BaseController.respond_success(
        {"service": settings.PROJECT_NAME, "api": settings.API_V1_PREFIX},
        "Tapafix API is running",
    )


app.include_router(api_router, prefix=settings.API_V1_PREFIX)

_web_dir = Path(__file__).resolve().parent.parent / "web"
if _web_dir.is_dir():
    app.mount(
        "/demo",
        StaticFiles(directory=str(_web_dir), html=True),
        name="demo",
    )
