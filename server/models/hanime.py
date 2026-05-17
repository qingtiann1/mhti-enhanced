"""Hanime data models for hanime-server API integration."""

from pydantic import BaseModel


class HanimeTag(BaseModel):
    name: str
    query: str


class HanimeStudio(BaseModel):
    name: str
    icon_url: str = ""
    url: str = ""


class HanimeVideoType(BaseModel):
    name: str
    query: str


class HanimeStreamUrl(BaseModel):
    quality: str
    url: str


class HanimeSeriesVideo(BaseModel):
    video_id: str
    title: str
    cover_url: str = ""
    duration: str = ""
    view_count: int = 0
    like_rate: str = ""
    like_count: int = 0
    studio: HanimeStudio | None = None


class HanimeRelatedVideo(BaseModel):
    video_id: str
    title: str
    cover_url: str = ""


class HanimeVideoDetail(BaseModel):
    """Full video detail from hanime-server API."""
    video_id: str
    title: str
    subtitle: str = ""
    cover_url: str = ""
    duration: str = ""
    view_count: int = 0
    like_rate: str = ""
    like_count: int = 0
    studio: HanimeStudio | None = None
    description: str = ""
    upload_date: str = ""
    video_type: HanimeVideoType | None = None
    tags: list[HanimeTag] = []
    series_videos: list[HanimeSeriesVideo] = []
    default_video_url: str = ""


class HanimeSearchResult(BaseModel):
    """Search result from hanime-server API."""
    video_id: str
    title: str
    cover_url: str = ""
    duration: str = ""
    view_count: int = 0
