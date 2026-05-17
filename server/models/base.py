"""Base model configurations for Pydantic models."""

from pydantic import BaseModel, ConfigDict


class AppBaseModel(BaseModel):
    """
    Base model with common configuration for all application models.

    Features:
    - Strip whitespace from strings
    - Validate assignments
    - Forbid extra fields
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )


class AppBaseModelLenient(BaseModel):
    """
    Base model with lenient configuration.

    Allows extra fields (useful for external API responses).
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="ignore",
    )
