from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


SortOrder = Literal["asc", "desc"]


class SubCategoryCreate(BaseModel):
    category_id: int
    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = Field(None, max_length=500)
    is_active: bool = True


class SubCategoryUpdate(BaseModel):
    category_id: int | None = None
    name: str | None = Field(None, min_length=1, max_length=120)
    description: str | None = Field(None, max_length=500)
    is_active: bool | None = None


class SubCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    name: str
    description: str | None
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    description: str | None = Field(None, max_length=500)
    is_active: bool = True


class CategoryUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    description: str | None = Field(None, max_length=500)
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    subcategories: list[SubCategoryResponse] | None = None
