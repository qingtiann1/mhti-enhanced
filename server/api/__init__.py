# API Routes Package
"""API routing utilities."""

import importlib
import pkgutil
from pathlib import Path
from typing import Generator

from fastapi import APIRouter


def auto_discover_routers() -> Generator[APIRouter, None, None]:
    """
    Automatically discover and yield all API routers.

    Scans the api/ directory for modules containing a 'router' attribute.

    Yields:
        APIRouter instances found in submodules.
    """
    api_dir = Path(__file__).parent

    for module_info in pkgutil.iter_modules([str(api_dir)]):
        if module_info.name.startswith("_"):
            continue

        module = importlib.import_module(f"server.api.{module_info.name}")

        if hasattr(module, "router"):
            yield module.router
