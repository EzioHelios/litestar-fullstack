"""System domain schemas."""

from app.domain.system.schemas._health import OAuthConfig, PublicAppConfig, SystemHealth

__all__ = (
    "OAuthConfig",
    "PublicAppConfig",
    "SystemHealth",
)
