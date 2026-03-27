# app/schemas/pagination.py
from pydantic import BaseModel, Field
from typing import TypeVar, Generic, Sequence

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number, starts at 1")
    page_size: int = Field(20, ge=1, le=100, description="Items per page, max 100")

    @property
    def offset(self) -> int:
        """SQL OFFSET = (page - 1) × page_size"""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response that works with any item type."""
    items: Sequence[T]
    total: int
    page: int
    page_size: int
    total_pages: int
