"""Standard API response models."""

from datetime import datetime
from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMeta(BaseModel):
    """Response metadata."""

    request_id: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""

    success: bool = True
    data: T
    meta: ResponseMeta | None = None


class PaginationInfo(BaseModel):
    """Pagination information."""

    page: int
    page_size: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated API response."""

    success: bool = True
    data: list[T]
    pagination: PaginationInfo
    meta: ResponseMeta | None = None


class ErrorDetail(BaseModel):
    """Error detail model."""

    code: str
    message: str
    details: dict | None = None


class ErrorResponse(BaseModel):
    """Standard error response."""

    success: bool = False
    error: ErrorDetail
