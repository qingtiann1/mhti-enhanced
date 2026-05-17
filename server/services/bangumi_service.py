"""Bangumi (bgm.tv) data source service for anime metadata."""

import logging
import re
from difflib import SequenceMatcher

import httpx

from server.models.bangumi import BangumiSearchResult, BangumiSearchResponse

logger = logging.getLogger(__name__)

BANGUMI_SEARCH_URL = "https://api.bgm.tv/search/subject"
BANGUMI_SUBJECT_URL = "https://api.bgm.tv/subject"
BANGUMI_V0_SUBJECT_URL = "https://api.bgm.tv/v0/subjects"

# Anime type
TYPE_ANIME = 2

# Common words to strip from search queries for better matching
CLEAN_PATTERNS = [
    re.compile(r"\[.*?\]"),
    re.compile(r"【.*?】"),
    re.compile(r"～.*?～"),
    re.compile(r"「.*?」"),
    re.compile(r"第\s*\d+\s*[話集话回章弾幕]"),
    re.compile(r"[Ff]it\.?\s*\d+"),
    re.compile(r"[Vv]ol\.?\s*\d+"),
    re.compile(r"[Ee][Pp]?\.?\s*\d+"),
    re.compile(r"OVA|OAD|ONA", re.I),
    re.compile(r"THE\s+ANIMATION", re.I),
    re.compile(r"\b\d{4}\b"),  # years
    re.compile(r"Season\s*\d+", re.I),
    re.compile(r"[Ss]\d{1,2}[Ee]\d{1,3}"),
]


class BangumiService:
    """Service for querying bgm.tv API as an anime metadata source."""

    def __init__(self, timeout: float = 15.0, access_token: str = ""):
        self.timeout = timeout
        self.access_token = access_token
        self._session_cookies: dict = {}

    @property
    def _auth_headers(self) -> dict:
        """Headers with optional Bearer token for authenticated requests."""
        headers = {"User-Agent": "MHTI/1.0"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    async def get_subject_detail(self, subject_id: int) -> dict | None:
        """Fetch full subject details from Bangumi v0 API.

        The v0 API returns summary, tags, rating, and other metadata
        not available in the search API. Requires auth for R18 content.

        Args:
            subject_id: The Bangumi subject ID.

        Returns:
            Subject detail dict or None on failure.
        """
        url = f"{BANGUMI_V0_SUBJECT_URL}/{subject_id}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(url, headers=self._auth_headers)
                if resp.status_code == 404:
                    logger.warning(f"Subject {subject_id} not found (may require auth)")
                    return None
                if resp.status_code != 200:
                    logger.warning(f"Subject API returned {resp.status_code}")
                    return None
                return resp.json()
        except Exception as e:
            logger.warning(f"Subject detail fetch failed: {e}")
            return None

    def enrich_search_result(
        self, result: BangumiSearchResult, detail: dict
    ) -> BangumiSearchResult:
        """Enrich a search result with data from the v0 subject detail API.

        The search API never returns summary; the v0 API does (with auth).
        """
        if detail:
            result.summary = detail.get("summary", result.summary)
            result.rating = detail.get("rating", result.rating)
            result.eps_count = detail.get("eps", detail.get("total_episodes", result.eps_count))
            # Update images if available
            images = detail.get("images")
            if images and not result.images:
                result.images = BangumiImage(
                    large=images.get("large", ""),
                    common=images.get("common", ""),
                    medium=images.get("medium", ""),
                    small=images.get("small", ""),
                    grid=images.get("grid", ""),
                )
        return result

    async def search_anime(
        self, query: str, max_results: int = 10
    ) -> list[BangumiSearchResult]:
        """Search bgm.tv for anime matching the query.

        Args:
            query: Search keywords.
            max_results: Maximum results to return.

        Returns:
            List of anime search results (type=2 only).
        """
        url = f"{BANGUMI_SEARCH_URL}/{query}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(
                    url,
                    headers={"User-Agent": "MHTI/1.0"},
                    cookies=self._session_cookies,
                )
                if resp.status_code != 200:
                    logger.warning(f"Bangumi search returned {resp.status_code}")
                    return []
                data = resp.json()
                if "error" in data:
                    logger.warning(f"Bangumi search error: {data.get('error')}")
                    return []
                # API returns 'list' key; map to items
                data["items"] = data.pop("list", [])
                response = BangumiSearchResponse(**data)
                # Filter anime type only, limit results
                anime_results = [r for r in response.items if r.type == TYPE_ANIME]
                return anime_results[:max_results]
        except Exception as e:
            logger.warning(f"Bangumi search failed: {e}")
            return []

    def clean_query(self, filename: str) -> str:
        """Clean a filename into a search query suitable for Bangumi.

        Removes brackets, episode markers, video IDs, and other noise.
        """
        query = filename
        for pat in CLEAN_PATTERNS:
            query = pat.sub(" ", query)
        # Remove hanime video_id prefix
        query = re.sub(r"^\d{5,7}_", "", query)
        # Normalize whitespace
        query = re.sub(r"\s+", " ", query).strip()
        return query

    def match_score(self, result: BangumiSearchResult, query: str) -> float:
        """Calculate match score between a search result and the query.

        Higher score = better match.
        """
        query_lower = query.lower().strip()
        name_lower = (result.name or "").lower()
        name_cn_lower = (result.name_cn or "").lower()

        # Exact match
        if query_lower == name_lower or query_lower == name_cn_lower:
            return 1.0

        # Contains match
        scores = []
        for name in [name_lower, name_cn_lower]:
            if name and query_lower:
                scores.append(SequenceMatcher(None, query_lower, name).ratio())

        base = max(scores) if scores else 0.0

        # Boost for results with more metadata
        if result.summary:
            base += 0.05
        if result.air_date:
            base += 0.05
        if result.eps_count and result.eps_count > 0:
            base += 0.02

        return min(base, 1.0)

    def get_best_match(
        self, results: list[BangumiSearchResult], query: str, threshold: float = 0.3
    ) -> BangumiSearchResult | None:
        """Select the best matching anime from search results.

        Args:
            results: Search results.
            query: Original query string.
            threshold: Minimum similarity score (0-1).

        Returns:
            Best match or None.
        """
        if not results:
            return None

        best = None
        best_score = 0.0
        for r in results:
            score = self.match_score(r, query)
            if score > best_score:
                best_score = score
                best = r

        if best and best_score >= threshold:
            logger.info(f"Bangumi best match: [{best.id}] {best.name_cn or best.name} (score={best_score:.2f})")
            return best
        return None

    def get_title(self, result: BangumiSearchResult) -> str:
        """Get the best display title (prefer Chinese name)."""
        return result.name_cn or result.name or "Unknown"

    def get_original_title(self, result: BangumiSearchResult) -> str:
        """Get the Japanese/original title."""
        if result.name_cn and result.name and result.name_cn != result.name:
            return result.name
        return ""

    def get_year(self, result: BangumiSearchResult) -> int | None:
        """Extract year from air_date."""
        if result.air_date:
            try:
                return int(result.air_date[:4])
            except (ValueError, IndexError):
                pass
        return None

    def get_cover_url(self, result: BangumiSearchResult) -> str:
        """Get the best cover image URL (HTTPS upgrade)."""
        if result.images:
            url = result.images.large or result.images.common or ""
            if url.startswith("http://"):
                url = "https://" + url[7:]
            return url
        return ""
