"""Static file serving for production environment."""

import mimetypes
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Default static files directory
DEFAULT_STATIC_DIR = "/app/static"

# Cache durations
CACHE_IMMUTABLE = "public, max-age=31536000, immutable"  # 1 year for hashed assets
CACHE_HTML = "no-cache"  # Always revalidate HTML

# File extensions that should have immutable cache
IMMUTABLE_EXTENSIONS = {".js", ".css", ".woff", ".woff2", ".ttf", ".eot", ".otf"}
CACHEABLE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".webp"}


def get_static_dir() -> Path:
    """Get static files directory from environment or default."""
    static_dir = os.getenv("STATIC_DIR", DEFAULT_STATIC_DIR)
    return Path(static_dir)


def get_cache_header(file_path: Path) -> str:
    """Determine appropriate cache header based on file type."""
    suffix = file_path.suffix.lower()
    if suffix in IMMUTABLE_EXTENSIONS or suffix in CACHEABLE_EXTENSIONS:
        return CACHE_IMMUTABLE
    if suffix == ".html":
        return CACHE_HTML
    return "public, max-age=3600"  # 1 hour default


def setup_static_files(app: FastAPI) -> bool:
    """
    Mount static files for production environment.

    Returns:
        True if static files were mounted, False otherwise.
    """
    static_dir = get_static_dir()

    if not static_dir.exists():
        return False

    index_file = static_dir / "index.html"
    if not index_file.exists():
        return False

    # Mount static assets (js, css, images, etc.)
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    return True


def setup_gzip_middleware(app: FastAPI) -> None:
    """Add Gzip compression middleware."""
    from fastapi.middleware.gzip import GZipMiddleware

    app.add_middleware(GZipMiddleware, minimum_size=1024)


def create_spa_handler(app: FastAPI) -> None:
    """
    Create SPA fallback handler for client-side routing.

    Must be called AFTER all API routes are registered.
    """
    static_dir = get_static_dir()
    index_file = static_dir / "index.html"

    if not index_file.exists():
        return

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(request: Request, full_path: str):
        """Serve SPA for all non-API routes."""
        # Skip API and WebSocket routes
        if full_path.startswith(("api/", "ws", "health")):
            return None

        # Try to serve static file first
        file_path = static_dir / full_path
        if file_path.is_file() and file_path.exists():
            media_type, _ = mimetypes.guess_type(str(file_path))
            return FileResponse(
                file_path,
                media_type=media_type,
                headers={"Cache-Control": get_cache_header(file_path)},
            )

        # Fallback to index.html for SPA routing
        return FileResponse(
            index_file,
            media_type="text/html",
            headers={"Cache-Control": CACHE_HTML},
        )
