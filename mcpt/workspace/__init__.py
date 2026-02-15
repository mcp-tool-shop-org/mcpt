"""Workspace configuration for MCP."""

from .config import (
    default_yaml,
    write_default,
    read_config,
    write_config,
    add_tool,
    remove_tool,
    grant_capability,
    revoke_capability,
    get_grants,
    read_lock,
    write_lock_record,
    get_ui_config,
    get_run_stats,
    get_all_run_stats,
    update_run_stats,
    MCP_YAML_FILENAME,
)

__all__ = [
    "default_yaml",
    "write_default",
    "read_config",
    "write_config",
    "add_tool",
    "remove_tool",
    "grant_capability",
    "revoke_capability",
    "get_grants",
    "read_lock",
    "write_lock_record",
    "get_ui_config",
    "get_run_stats",
    "get_all_run_stats",
    "update_run_stats",
    "MCP_YAML_FILENAME",
]
