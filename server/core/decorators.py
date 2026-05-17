"""Dependency injection decorators."""

from typing import TypeVar, Type, Callable
from server.core.container import Scope, get_container

T = TypeVar("T")


def injectable(scope: Scope = Scope.SINGLETON) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator to mark a class as injectable service.

    Args:
        scope: Service lifecycle scope (SINGLETON or TRANSIENT)

    Usage:
        @injectable(scope=Scope.SINGLETON)
        class ConfigService:
            ...
    """
    def decorator(cls: Type[T]) -> Type[T]:
        container = get_container()
        container.register_type(cls, cls, scope)
        return cls
    return decorator
