# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | Yes       |

## Reporting a Vulnerability

Email: **64996768+mcp-tool-shop@users.noreply.github.com**

Include:
- Description of the vulnerability
- Steps to reproduce
- Version affected
- Potential impact

### Response timeline

| Action | Target |
|--------|--------|
| Acknowledge report | 48 hours |
| Assess severity | 7 days |
| Release fix | 30 days |

## Scope

mcpt is a **CLI tool** for discovering and running MCP Tool Shop tools.

- **Data touched:** Registry metadata (fetched from GitHub). Local workspace config (`mcp.yaml`). Tool install artifacts in platform cache directory
- **Data NOT touched:** No telemetry. No analytics. No credentials stored. No user data collected
- **Network:** HTTPS to GitHub for registry metadata. Optional tool installation from npm/PyPI
- **Permissions:** Read: registry metadata. Write: local cache directory, workspace `mcp.yaml`
- **No telemetry** is collected or sent
