from pydantic import BaseModel
from typing import Any, List, Dict, Any
from typing import Generic, TypeVar

T = TypeVar('T')

class BaseResponse(BaseModel, Generic[T]):
    statusCode: int
    message: str
    status: bool
    response: Dict[str, T] = {"data": None}
    errors: List[str] = []

    class Config:
        from_attributes = True

class PaginatedResponse(BaseResponse[List[T]]):
    response: Dict[str, list[T]] = {"data": []}

