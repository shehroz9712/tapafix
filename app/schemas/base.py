from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    statusCode: int
    message: str
    status: bool
    response: dict[str, Any] = Field(default_factory=lambda: {"data": None})
    errors: list[Any] = Field(default_factory=list)

    model_config = {"from_attributes": True}
