"""Database connection and session management - compatibility layer.

This module re-exports from server.core.db for backward compatibility.
New code should import directly from server.core.db.
"""

from server.core.db import (
    DATABASE_PATH,
    DatabaseManager,
    close_database,
    configure_connection,
    get_db,
    get_db_manager,
    init_database,
)

# Re-export for backward compatibility
__all__ = [
    "DATABASE_PATH",
    "DatabaseManager",
    "close_database",
    "get_db",
    "get_db_manager",
    "init_database",
]


# Legacy function alias
async def _configure_connection(db):
    """Legacy wrapper for configure_connection."""
    await configure_connection(db)
