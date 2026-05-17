"""Service interfaces for dependency inversion."""

from .config import IConfigService
from .tmdb import ITMDBService

__all__ = ["IConfigService", "ITMDBService"]
