from __future__ import annotations

from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.schemas.base import BaseResponse


class BaseController:
    """Standard API envelope for all HTTP responses.

    Domain controllers should inherit this class and call ``self.respond_*``
    so every endpoint returns the same ``BaseResponse`` shape.
    """

    @staticmethod
    def _response_content(body: BaseResponse) -> dict[str, Any]:
        content = jsonable_encoder(body.model_dump())
        if content.get("errors") is None:
            content.pop("errors", None)
        return content

    @staticmethod
    def respond_success(
        data: Any = None,
        message: str = "Success",
        status_code: int = 200,
    ) -> JSONResponse:
        body = BaseResponse(
            success=True,
            message=message,
            data=data,
        )
        return JSONResponse(
            status_code=status_code,
            content=BaseController._response_content(body),
        )

    @staticmethod
    def respond_bad_request(
        message: str = "Bad request", errors: Any | None = None
    ) -> JSONResponse:
        return BaseController._error(message, 400, errors)

    @staticmethod
    def respond_unauthorized(
        message: str = "Unauthorized", errors: Any | None = None
    ) -> JSONResponse:
        return BaseController._error(message, 401, errors)

    @staticmethod
    def respond_forbidden(
        message: str = "Forbidden", errors: Any | None = None
    ) -> JSONResponse:
        return BaseController._error(message, 403, errors)

    @staticmethod
    def respond_not_found(
        message: str = "Not found", errors: Any | None = None
    ) -> JSONResponse:
        return BaseController._error(message, 404, errors)

    @staticmethod
    def respond_conflict(
        message: str = "Conflict", errors: Any | None = None
    ) -> JSONResponse:
        return BaseController._error(message, 409, errors)

    @staticmethod
    def respond_validation_error(
        message: str = "Validation error", errors: Any | None = None
    ) -> JSONResponse:
        return BaseController._error(message, 422, errors)

    @staticmethod
    def respond_internal_error(
        message: str = "Internal server error", errors: Any | None = None
    ) -> JSONResponse:
        return BaseController._error(message, 500, errors)

    @staticmethod
    def _error(
        message: str, status_code: int, errors: Any | None
    ) -> JSONResponse:
        body = BaseResponse(
            success=False,
            message=message,
            data=None,
            errors=errors,
        )
        return JSONResponse(
            status_code=status_code,
            content=BaseController._response_content(body),
        )
