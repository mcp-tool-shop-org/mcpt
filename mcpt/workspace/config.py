"""Workspace configuration (mcp.yaml) management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import json
from datetime import datetime, timezone
import yaml

from mcpt.registry.client import DEFAULT_REGISTRY_SOURCE, DEFAULT_REF

MCP_YAML_FILENAME = "mcp.yaml"
MCP_LOCK_FILENAME = "mcp.lock.yaml"
MCP_STATE_FILENAME = "mcp.state.json"

def update_run_stats(path: Path, tool_id: str, success: bool) -> None:
    """Update execution statistics for a tool."""
    state_path = path.parent / MCP_STATE_FILENAME
    
    data = {}
    if state_path.exists():
        try:
            data = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            pass
            
    if "stats" not in data:
        data["stats"] = {}
        
    stats = data["stats"].get(tool_id, {
        "runs_ok": 0,
        "runs_failed": 0,
        "last_run_at": None
    })
    
    if success:
        stats["runs_ok"] += 1
    else:
        stats["runs_failed"] += 1
        
    stats["last_run_at"] = datetime.now(timezone.utc).isoformat()
    
    data["stats"][tool_id] = stats
    
    state_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_all_run_stats(path: Path) -> dict[str, dict[str, Any]]:
    """Get all execution statistics."""
    state_path = path.parent / MCP_STATE_FILENAME
    if not state_path.exists():
        return {}
        
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
        return data.get("stats", {})
    except Exception:
        return {}


def get_run_stats(path: Path, tool_id: str) -> dict[str, Any]:
    """Get execution statistics for a tool."""
    state_path = path.parent / MCP_STATE_FILENAME
    if not state_path.exists():
        return {}
        
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
        return data.get("stats", {}).get(tool_id, {})
    except Exception:
        return {}


def default_yaml(registry_source: str, registry_ref: str) -> str:
    """Generate default mcp.yaml content."""
    return (
        'schema_version: "0.1"\n'
        'name: "my-mcp-workspace"\n\n'
        "registry:\n"
        f'  source: "{registry_source}"\n'
        f'  ref: "{registry_ref}"\n\n'
        "tools: []\n\n"
        "run:\n"
        "  safe_by_default: true\n"
    )


def write_default(
    path: Path,
    registry_source: str = DEFAULT_REGISTRY_SOURCE,
    registry_ref: str = DEFAULT_REF,
) -> None:
    """Write default mcp.yaml to path."""
    path.write_text(default_yaml(registry_source, registry_ref), encoding="utf-8")


def read_config(path: Path) -> dict[str, Any]:
    """Read mcp.yaml configuration."""
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def write_config(path: Path, config: dict[str, Any]) -> None:
    """Write configuration to mcp.yaml."""
    path.write_text(
        yaml.dump(config, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def add_tool(path: Path, tool_id: str, ref: str | None = None) -> bool:
    """Add a tool to the workspace configuration.

    Returns True if the tool was added, False if it already exists.
    """
    config = read_config(path)
    tools = config.get("tools", [])

    # Check if tool already exists
    for tool in tools:
        if isinstance(tool, str) and tool == tool_id:
            return False
        if isinstance(tool, dict) and tool.get("id") == tool_id:
            return False

    # Add the tool
    if ref:
        tools.append({"id": tool_id, "ref": ref})
    else:
        tools.append(tool_id)

    config["tools"] = tools
    write_config(path, config)
    return True


def remove_tool(path: Path, tool_id: str) -> bool:
    """Remove a tool from the workspace configuration.

    Returns True if the tool was removed, False if it wasn't found.
    """
    config = read_config(path)
    tools = config.get("tools", [])
    original_len = len(tools)

    # Filter out the tool
    new_tools = []
    for tool in tools:
        if isinstance(tool, str) and tool == tool_id:
            continue
        if isinstance(tool, dict) and tool.get("id") == tool_id:
            continue
        new_tools.append(tool)

    if len(new_tools) == original_len:
        return False

    config["tools"] = new_tools
    write_config(path, config)
    return True


def grant_capability(path: Path, tool_id: str, capability: str) -> bool:
    """Grant a capability to a tool in the workspace configuration."""
    config = read_config(path)
    tools = config.get("tools", [])
    
    found = False
    new_tools = []
    
    for tool in tools:
        if isinstance(tool, str):
            if tool == tool_id:
                # Upgrade to dict
                tool = {"id": tool, "grants": [capability]}
                found = True
            new_tools.append(tool)
        elif isinstance(tool, dict):
            if tool.get("id") == tool_id:
                grants = tool.get("grants", [])
                if capability not in grants:
                    grants.append(capability)
                tool["grants"] = grants
                found = True
            new_tools.append(tool)
    
    if not found:
        return False
        
    config["tools"] = new_tools
    write_config(path, config)
    return True


def revoke_capability(path: Path, tool_id: str, capability: str) -> bool:
    """Revoke a capability from a tool in the workspace configuration."""
    config = read_config(path)
    tools = config.get("tools", [])
    
    found = False
    new_tools = []
    
    for tool in tools:
        if isinstance(tool, str):
            if tool == tool_id:
                found = True # Exists, but has no grants to revoke
            new_tools.append(tool)
        elif isinstance(tool, dict):
            if tool.get("id") == tool_id:
                grants = tool.get("grants", [])
                if capability in grants:
                    grants.remove(capability)
                    found = True
                tool["grants"] = grants
            new_tools.append(tool)
            
    if not found:
        return False
        
    config["tools"] = new_tools
    write_config(path, config)
    return True


def get_grants(path: Path, tool_id: str) -> list[str]:
    """Get granted capabilities for a tool."""
    try:
        config = read_config(path)
        for tool in config.get("tools", []):
            if isinstance(tool, str) and tool == tool_id:
                return []
            if isinstance(tool, dict) and tool.get("id") == tool_id:
                return tool.get("grants", [])
        return []
    except Exception:
        return []


def read_lock(path: Path) -> dict[str, Any]:
    """Read mcp.lock.yaml configuration."""
    lock_path = path.parent / MCP_LOCK_FILENAME
    if not lock_path.exists():
        return {"tools": {}}
    return yaml.safe_load(lock_path.read_text(encoding="utf-8")) or {"tools": {}}


def write_lock_record(
    path: Path,
    tool_id: str,
    record: dict[str, Any],
) -> None:
    """Update install record in mcp.lock.yaml."""
    lock_path = path.parent / MCP_LOCK_FILENAME
    
    lock_data = {"tools": {}}
    if lock_path.exists():
        lock_data = yaml.safe_load(lock_path.read_text(encoding="utf-8")) or {"tools": {}}
        
    lock_data["tools"][tool_id] = record
    
    # Sort keys for deterministic output
    lock_data["tools"] = dict(sorted(lock_data["tools"].items()))
    
    lock_path.write_text(
        yaml.dump(lock_data, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def get_ui_config(path: Path) -> dict[str, Any]:
    """Get UI configuration from mcp.yaml settings."""
    # We allow 'ui' section in mcp.yaml or global config potentially
    # For now, mcp.yaml
    if not path.exists():
        return {}
    try:
        data = read_config(path)
        return data.get("ui", {})
    except Exception:
        return {}
