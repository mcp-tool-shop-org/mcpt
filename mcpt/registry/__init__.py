"""Registry client for MCP tool registry."""

from .client import (
    RegistryConfig,
    RegistryFetchError,
    RegistryStatus,
    fetch_registry,
    get_registry,
    get_registry_status,
    get_tool,
    load_cached_registry,
    save_cached_registry,
    search_tools,
    load_cached_artifact,
    get_bundle_membership,
)
from .featured import get_featured, FeaturedData, Section, Collection

__all__ = [
    "RegistryConfig",
    "RegistryFetchError",
    "RegistryStatus",
    "fetch_registry",
    "get_registry",
    "get_registry_status",
    "get_tool",
    "load_cached_registry",
    "save_cached_registry",
    "search_tools",
    "load_cached_artifact",
    "get_bundle_membership",
    "get_featured",
]
