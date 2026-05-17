"""Data models for subtitle processing."""

from enum import Enum

from pydantic import BaseModel


class SubtitleLanguage(str, Enum):
    """Subtitle language identifiers."""

    CHS = "chs"  # Simplified Chinese
    CHT = "cht"  # Traditional Chinese
    ENG = "eng"  # English
    JPN = "jpn"  # Japanese
    KOR = "kor"  # Korean
    UNKNOWN = ""  # Unknown


class SubtitleFile(BaseModel):
    """Subtitle file information."""

    path: str
    filename: str
    extension: str
    language: SubtitleLanguage | None = None
    associated_video: str | None = None


class SubtitleScanRequest(BaseModel):
    """Request to scan for subtitles."""

    folder_path: str


class SubtitleScanResponse(BaseModel):
    """Response with scanned subtitles."""

    subtitles: list[SubtitleFile]
    total: int


class SubtitleAssociateRequest(BaseModel):
    """Request to associate subtitles with videos."""

    folder_path: str
    video_files: list[str] | None = None  # If None, auto-detect


class VideoSubtitleAssociation(BaseModel):
    """Association between a video and its subtitles."""

    video: str
    video_path: str
    subtitles: list[SubtitleFile]


class SubtitleAssociateResponse(BaseModel):
    """Response with video-subtitle associations."""

    associations: list[VideoSubtitleAssociation]


class SubtitleRenameRequest(BaseModel):
    """Request to rename subtitle file."""

    subtitle_path: str
    new_video_name: str  # New video filename (without extension)
    preserve_language: bool = True


class SubtitleRenameResult(BaseModel):
    """Result of subtitle rename."""

    source_path: str
    dest_path: str
    success: bool
    error: str | None = None


class BatchSubtitleRenameRequest(BaseModel):
    """Batch subtitle rename request."""

    items: list[SubtitleRenameRequest]


class BatchSubtitleRenameResponse(BaseModel):
    """Batch subtitle rename response."""

    total: int
    success: int
    failed: int
    results: list[SubtitleRenameResult]
