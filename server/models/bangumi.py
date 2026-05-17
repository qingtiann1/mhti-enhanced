"""Bangumi (bgm.tv) data models."""

from pydantic import BaseModel


class BangumiImage(BaseModel):
    large: str = ""
    common: str = ""
    medium: str = ""
    small: str = ""
    grid: str = ""


class BangumiSearchResult(BaseModel):
    """Search result from bgm.tv API."""
    id: int
    url: str = ""
    type: int  # 1=book, 2=anime, 3=music, 4=game, 6=real
    name: str = ""
    name_cn: str = ""
    summary: str = ""
    air_date: str = ""
    air_weekday: int = 0
    images: BangumiImage | None = None
    eps: int = 0
    eps_count: int = 0
    rating: dict | None = None


class BangumiSearchResponse(BaseModel):
    """Search response wrapper."""
    results: int = 0
    items: list[BangumiSearchResult] = []
