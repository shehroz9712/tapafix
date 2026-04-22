from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Any = None
    errors: Any = None

    model_config = {"from_attributes": True}
