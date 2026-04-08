from schemas.base import BaseResponse
from typing import Any, Dict, List, Generic, TypeVar
import status

T = TypeVar('T')

class BaseController(Generic[T]):
    @staticmethod
    def success(data: Any = None, message: str = "Success", status_code: int = 200) -> BaseResponse[T]:
        return BaseResponse[T](
            statusCode=status_code,
            message=message,
            status=True,
            response={"data": data},
            errors=[]
        )

    @staticmethod
    def error(message: str, errors: List[str] = None, status_code: int = 400) -> BaseResponse[T]:
        return BaseResponse[T](
            statusCode=status_code,
            message=message,
            status=False,
            response={"data": None},
            errors=errors or []
        )

    @staticmethod
    def not_found(message: str = "Not found") -> BaseResponse[T]:
        return BaseController.error(message, status_code=404)

    @staticmethod
    def unauthorized(message: str = "Unauthorized") -> BaseResponse[T]:
        return BaseController.error(message, status_code=401)

    @staticmethod
    def forbidden(message: str = "Forbidden") -> BaseResponse[T]:
        return BaseController.error(message, status_code=403)

    @staticmethod
    def server_error(message: str = "Internal server error") -> BaseResponse[T]:
        return BaseController.error(message, status_code=500)

