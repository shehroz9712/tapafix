from __future__ import annotations

class AppException(Exception):
    """Domain / application error with HTTP mapping hints."""

    def __init__(self, message: str, status_code: int = 400, errors: list | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors or []


class BadRequestError(AppException):
    """HTTP 400 — use from services; handled globally via BaseController."""

    def __init__(self, message: str = "Bad request", errors: list | None = None):
        super().__init__(message, status_code=400, errors=errors)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Unauthorized", errors: list | None = None):
        super().__init__(message, status_code=401, errors=errors)


class ForbiddenError(AppException):
    def __init__(self, message: str = "Forbidden", errors: list | None = None):
        super().__init__(message, status_code=403, errors=errors)


class NotFoundError(AppException):
    def __init__(self, message: str = "Not found", errors: list | None = None):
        super().__init__(message, status_code=404, errors=errors)


class ConflictError(AppException):
    def __init__(self, message: str = "Conflict", errors: list | None = None):
        super().__init__(message, status_code=409, errors=errors)
