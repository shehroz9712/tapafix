from typing import Generic, TypeVar, Sequence
from math import ceil
from pydantic import BaseModel

T = TypeVar('T')

class Pagination(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    limit: int
    pages: int

def paginate(items: Sequence[T], page: int = 1, limit: int = 10) -> Pagination[T]:
    total = len(items)
    pages = ceil(total / limit)
    start = (page - 1) * limit
    end = start + limit
    return Pagination(
        items=items[start:end],
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )

