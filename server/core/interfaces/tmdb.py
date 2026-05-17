"""TMDBService interface definition."""

from typing import Protocol

from server.models.tmdb import TMDBSearchResponse, TMDBSeries, TMDBSeason


class ITMDBService(Protocol):
    """Interface for TMDB service."""

    async def search_series(self, query: str, year: int | None = None) -> TMDBSearchResponse:
        """Search for TV series."""
        ...

    async def get_series_details(self, series_id: int) -> TMDBSeries:
        """Get series details by ID."""
        ...

    async def get_season_details(self, series_id: int, season_number: int) -> TMDBSeason:
        """Get season details."""
        ...
