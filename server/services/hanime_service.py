"""Hanime data source service - queries local hanime-server for metadata."""

import logging
import os
import re

import httpx

from server.models.hanime import HanimeVideoDetail

logger = logging.getLogger(__name__)

HANIME_ID_PATTERN = re.compile(r"^(\d{5,7})_")

DEFAULT_HANIME_URL = os.environ.get("HANIME_API_URL", "http://localhost:8000")


class HanimeService:
    """Service for querying hanime-server API as a metadata source."""

    def __init__(self, base_url: str | None = None, timeout: float = 30.0):
        self.base_url = (base_url or DEFAULT_HANIME_URL).rstrip("/")
        self.timeout = timeout

    @staticmethod
    def extract_video_id(filename: str) -> str | None:
        """Extract hanime video_id from filename.

        Filenames follow the pattern: {video_id}_{rest}.mp4
        e.g. "100012_妻NTR・零 -我的过错 她的选择- [中文字幕].mp4"
        """
        m = HANIME_ID_PATTERN.match(filename)
        if m:
            return m.group(1)
        return None

    @staticmethod
    def looks_like_hanime(filename: str) -> bool:
        """Check if filename looks like a hanime-downloaded file."""
        return HANIME_ID_PATTERN.match(filename) is not None

    async def get_video_detail(self, video_id: str) -> HanimeVideoDetail | None:
        """Get full video metadata from hanime-server API.

        Args:
            video_id: The hanime video ID.

        Returns:
            HanimeVideoDetail if found, None otherwise.
        """
        url = f"{self.base_url}/api/videos/detail/{video_id}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    return HanimeVideoDetail(**data)
                elif resp.status_code == 404:
                    logger.info(f"Hanime video {video_id} not found")
                    return None
                else:
                    logger.warning(f"Hanime API returned {resp.status_code} for {video_id}")
                    return None
        except httpx.TimeoutException:
            logger.warning(f"Hanime API timeout for {video_id}")
            return None
        except httpx.RequestError as e:
            logger.warning(f"Hanime API request failed for {video_id}: {e}")
            return None

    def get_series_name(self, detail: HanimeVideoDetail) -> str:
        """Extract series name from video detail.

        Uses subtitle (Chinese name) if available, otherwise title (Japanese name).
        Strips episode numbers, volume markers, season markers, and whitespace.
        """
        name = detail.subtitle or detail.title
        name = name.strip()

        # Strip episode/volume/season markers from the end
        import re
        patterns = [
            r"\s+第?\s*\d+\s*[話集话回章弾幕期季卷冊]$",  # 第1話, 第2集, 第3期
            r"\s+\d+\s*$",                              # " 1", " 12"
            r"\s+[Ff]it\.?\s*\d+\s*$",                  # " Fit. 1"
            r"\s+[Vv]ol\.?\s*\d+\s*$",                  # " Vol. 1"
            r"\s+[Ee][Pp]\.?\s*\d+\s*$",               # " EP. 1"
            r"\s+#\s*\d+\s*$",                          # " #1"
            r"\s+[Ss]eason\s*\d+\s*$",                  # " Season 1"
            r"\s+Season\s*\d+\s*$",                     # "Season 1" (no leading space)
        ]
        for pat in patterns:
            name = re.sub(pat, "", name)

        return name.strip()

    def get_episode_number(self, detail: HanimeVideoDetail) -> int:
        """Extract episode number from video detail.

        Looks at the title for episode numbers, defaults to 1.
        """
        title = detail.title or ""
        # Match patterns like " 1", "第1話", "第1集", "Fit.1", "Vol.1", etc.
        import re
        patterns = [
            r"\s+(\d+)\s*$",
            r"第\s*(\d+)\s*[話集话回章弾幕]",
            r"[Ff]it\.?\s*(\d+)",
            r"[Vv]ol\.?\s*(\d+)",
            r"[Ee][Pp]?\.?\s*(\d+)",
            r"#\s*(\d+)",
        ]
        for pat in patterns:
            m = re.search(pat, title)
            if m:
                return int(m.group(1))
        return 1

    def get_genres(self, detail: HanimeVideoDetail) -> list[str]:
        """Extract genres as list of tag names."""
        return [t.name for t in detail.tags]

    def get_year(self, detail: HanimeVideoDetail) -> int | None:
        """Extract year from upload_date."""
        if detail.upload_date:
            try:
                from datetime import date
                return date.fromisoformat(detail.upload_date[:10]).year
            except (ValueError, IndexError):
                pass
        return None
