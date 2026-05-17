"""Authentication dependencies for API protection."""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from server.services.auth_service import auth_service

security = HTTPBearer(auto_error=False)


class AuthContext:
    """Authentication context with user info."""

    def __init__(self, username: str, session_id: str):
        self.username = username
        self.session_id = session_id


async def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AuthContext:
    """
    Dependency that requires valid authentication.

    Returns:
        AuthContext with username and session_id.

    Raises:
        HTTPException: 401 if not authenticated.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证信息",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username, session_id = auth_service.verify_token(credentials.credentials)
    if not username or not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthContext(username=username, session_id=session_id)


async def optional_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> AuthContext | None:
    """
    Dependency that optionally validates authentication.

    Returns:
        AuthContext if authenticated, None otherwise.
    """
    if not credentials:
        return None

    username, session_id = auth_service.verify_token(credentials.credentials)
    if not username or not session_id:
        return None

    return AuthContext(username=username, session_id=session_id)


def get_client_ip(request: Request) -> str:
    """Get client IP from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
