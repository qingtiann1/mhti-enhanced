"""Image download data models."""

from enum import Enum

from pydantic import BaseModel


class ImageType(str, Enum):
    """Image type enumeration."""

    POSTER = "poster"
    BACKDROP = "backdrop"
    STILL = "still"  # Episode thumbnail
    SEASON_POSTER = "season_poster"


class ImageSize(str, Enum):
    """TMDB image size options."""

    W92 = "w92"
    W154 = "w154"
    W185 = "w185"
    W342 = "w342"
    W500 = "w500"
    W780 = "w780"
    ORIGINAL = "original"


class ImageDownloadRequest(BaseModel):
    """Single image download request."""

    url: str
    save_path: str
    filename: str


class ImageDownloadResult(BaseModel):
    """Download result for a single image."""

    url: str
    save_path: str
    success: bool
    error: str | None = None


class BatchDownloadRequest(BaseModel):
    """Batch download request."""

    images: list[ImageDownloadRequest]
    concurrency: int = 3


class BatchDownloadResponse(BaseModel):
    """Batch download response."""

    total: int
    success: int
    failed: int
    results: list[ImageDownloadResult]
