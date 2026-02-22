# mcpt

## What This Does

MCP Tool Shop's core CLI and metadata publishing system.
Central hub for tool discovery, registry, and ecosystem management.

## Tools & Commands

- `mcpt list` — List all available tools
- `mcpt search` — Search tools by name/capability
- `mcpt info` — Get tool details
- `mcpt install` — Install a tool
- `mcpt registry` — Manage tool registries

## Architecture

- Plugin discovery and registration
- Tool metadata management
- Registry synchronization
- Version management

## Dependencies

- Python >= 3.11
- mcp >= 1.0.0

## Key Notes

- Central registry for mcp-tool-shop-org tools
- Integrates with gh CLI for org management
- Publishes metadata to multiple destinations
- Supports multiple package managers (pip, npm, brew, etc.)
