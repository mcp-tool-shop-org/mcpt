"""Registry client with GitHub fetch and local caching."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from platformdirs import user_cache_dir

# Registry defaults - pin to stable release for new workspaces
DEFAULT_REGISTRY_SOURCE = "https://github.com/mcp-tool-shop-org/mcp-tool-registry"
DEFAULT_REF = "v0.3.0"


def github_raw_registry_url(source: str, ref: str) -> str:
    """Convert GitHub repo URL to raw registry.json URL."""
    parts = source.rstrip("/").split("/")
    org, repo = parts[-2], parts[-1]
    return f"https://raw.githubusercontent.com/{org}/{repo}/{ref}/registry.json"


@dataclass(frozen=True)
class RegistryConfig:
    """Configuration for registry source."""

    source: str = DEFAULT_REGISTRY_SOURCE
    ref: str = DEFAULT_REF


def registry_cache_path(cfg: RegistryConfig) -> Path:
    """Get the cache path for the registry."""
    base = Path(user_cache_dir("mcp", "mcp-tool-shop"))
    return base / "registry" / cfg.ref / "registry.json"


def load_cached_registry(cfg: RegistryConfig) -> dict[str, Any] | None:
    """Load registry from local cache if available.

    Returns None if cache doesn't exist or is corrupted.
    Corrupted cache files are automatically deleted for self-healing.
    """
    p = registry_cache_path(cfg)
    if not p.exists():
        return None

    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        # Validate basic structure
        if not isinstance(data, dict) or "tools" not in data:
            raise ValueError("Invalid registry structure")
        return data
    except (json.JSONDecodeError, ValueError, OSError) as e:
        # Corrupted cache - delete and return None for self-healing
        try:
            p.unlink()
        except OSError:
            pass
        return None


def save_cached_registry(cfg: RegistryConfig, data: dict[str, Any]) -> None:
    """Save registry to local cache."""
    p = registry_cache_path(cfg)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def load_local_registry(path: Path) -> dict[str, Any]:
    """Load registry from a local file."""
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_registry(cfg: RegistryConfig) -> dict[str, Any]:
    """Fetch registry from GitHub or local file."""
    # Support local file paths
    source_path = Path(cfg.source)
    if source_path.exists() and source_path.is_file():
        return load_local_registry(source_path)

    url = github_raw_registry_url(cfg.source, cfg.ref)
    r = httpx.get(url, timeout=20.0)
    r.raise_for_status()
    data = r.json()

    # Fetch additional artifacts (best effort)
    try:
        # registry.json is at .../ref/registry.json
        # artifacts are at .../ref/dist/...
        base_url = url.rsplit("/", 1)[0]

        # Cache directory: .../registry/ref/dist/
        cache_base = registry_cache_path(cfg).parent / "dist"
        cache_base.mkdir(parents=True, exist_ok=True)

        artifacts = [
            "registry.index.json",
            "capabilities.json",
            "featured.json",
            "registry.report.json",
            "registry.llms.txt",
        ]

        for art in artifacts:
            try:
                resp = httpx.get(f"{base_url}/dist/{art}", timeout=10.0)
                if resp.status_code == 200:
                    (cache_base / art).write_bytes(resp.content)
            except Exception:
                pass

    except Exception:
        # Ensure we return the main registry even if artifact fetching fails
        pass

    return data


class RegistryFetchError(Exception):
    """Error fetching registry from remote."""

    def __init__(self, message: str, cached_available: bool = False):
        super().__init__(message)
        self.cached_available = cached_available


def get_registry(
    cfg: RegistryConfig | None = None,
    force_refresh: bool = False,
) -> dict[str, Any]:
    """Get registry, using cache if available unless force_refresh is True.

    On network failure:
    - If cache exists, returns cached data (graceful degradation)
    - If no cache, raises RegistryFetchError with helpful message
    """
    if cfg is None:
        cfg = RegistryConfig()

    cached = load_cached_registry(cfg)

    if not force_refresh and cached is not None:
        return cached

    try:
        data = fetch_registry(cfg)
        save_cached_registry(cfg, data)
        return data
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        if cached is not None:
            # Graceful degradation - return stale cache
            return cached
        raise RegistryFetchError(
            f"Failed to fetch registry: {e}\n"
            f"No cached registry available. Check your network connection.",
            cached_available=False,
        ) from e


def get_tool(tool_id: str, cfg: RegistryConfig | None = None) -> dict[str, Any] | None:
    """Get a specific tool by ID."""
    registry = get_registry(cfg)
    for tool in registry.get("tools", []):
        if tool.get("id") == tool_id:
            return tool
    return None


def load_cached_artifact(cfg: RegistryConfig, filename: str) -> Any | None:
    """Load a cached artifact (JSON or text) if available."""
    p = registry_cache_path(cfg).parent / "dist" / filename
    if not p.exists():
        return None
    try:
        content = p.read_text(encoding="utf-8")
        if filename.endswith(".json"):
            return json.loads(content)
        return content
    except Exception:
        return None


def get_bundle_membership(cfg: RegistryConfig | None = None) -> dict[str, list[str]]:
    """Return a mapping of tool_id -> list[bundle_names] for all tools."""
    if cfg is None:
        cfg = RegistryConfig()
    try:
        index = load_cached_artifact(cfg, "registry.index.json")
        if not index or "bundles" not in index:
            return {}
        
        # Invert: tool_id -> bundles
        mapping: dict[str, list[str]] = {}
        for bundle_name, tools in index["bundles"].items():
            for tool_id in tools:
                if tool_id not in mapping:
                    mapping[tool_id] = []
                mapping[tool_id].append(bundle_name)
        return mapping
    except Exception:
        return {}


def calculate_match_score(tool: dict[str, Any], query_lower: str) -> tuple[int, list[str]]:
    """Calculate match score and reasons for a tool."""
    score = 0
    reasons = []
    
    tid = tool.get("id", "").lower()
    name = tool.get("name", "").lower()
    desc = tool.get("description", "").lower()
    tags = [t.lower() for t in tool.get("tags", [])]

    # 1. Exact ID match (100)
    if tid == query_lower:
        score += 100
        reasons.append("exact id match")
    
    # 2. Exact keyword match in name (80)
    if query_lower == name:
        score += 80
        reasons.append("exact name match")

    # 3. Exact tag match (60)
    if query_lower in tags:
        score += 60
        reasons.append(f"exact tag match: {query_lower}")

    # 4. ID Prefix match (40)
    if tid.startswith(query_lower):
        score += 40
        reasons.append("id prefix match")

    # 5. Name/Desc substring (20)
    if query_lower in name:
        score += 20
        reasons.append("name substring match")
    if query_lower in desc:
        score += 10
        reasons.append("description substring match")
        
    # 6. Tag substring (5 per tag)
    for tag in tags:
        if query_lower in tag:
            score += 5
            reasons.append(f"tag substring match: {tag}")
            
    return score, reasons


def search_tools(
    query: str,
    cfg: RegistryConfig | None = None,
    bundle: str | None = None,
    tag: str | None = None,
) -> list[dict[str, Any]]:
    """Search tools with ranking and filtering.
    
    Returns tools with injected '_score' and '_reasons' fields.
    """
    registry = get_registry(cfg)
    query_lower = query.lower() if query else ""
    results = []

    # Try to load index for better bundle/tag data, but fallback to registry.json
    index = load_cached_artifact(cfg or RegistryConfig(), "registry.index.json")
    
    # If bundle filter requested, and we have index with bundles
    allowed_ids = None
    if bundle and index and "bundles" in index:
        allowed_ids = set(index["bundles"].get(bundle, []))
    
    for tool in registry.get("tools", []):
        # Filter by bundle
        if allowed_ids is not None and tool.get("id") not in allowed_ids:
            continue
            
        # Filter by tag
        if tag and tag.lower() not in [t.lower() for t in tool.get("tags", [])]:
            continue

        if not query:
            # If no query but filters matched, add with zero score
            tool_copy = tool.copy()
            tool_copy["_score"] = 0
            tool_copy["_reasons"] = ["filter match"]
            results.append(tool_copy)
            continue

        score, reasons = calculate_match_score(tool, query_lower)
        if score > 0:
            tool_copy = tool.copy()
            tool_copy["_score"] = score
            tool_copy["_reasons"] = reasons
            results.append(tool_copy)

    # Sort by score descending, then ID ascending
    results.sort(key=lambda x: (-x.get("_score", 0), x.get("id", "")))
    
    return results


@dataclass
class RegistryStatus:
    """Status information about the registry."""

    source: str
    ref: str
    cache_path: Path
    cache_exists: bool
    cache_mtime: datetime | None
    tool_count: int
    provenance: str  # "cache", "remote", "local_file", "not_loaded"


def get_registry_status(cfg: RegistryConfig | None = None) -> RegistryStatus:
    """Get status information about the registry without fetching."""
    if cfg is None:
        cfg = RegistryConfig()

    cache_path = registry_cache_path(cfg)
    cache_exists = cache_path.exists()
    cache_mtime = None
    tool_count = 0
    provenance = "not_loaded"

    if cache_exists:
        cache_mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            tool_count = len(data.get("tools", []))
            provenance = "cache"
        except Exception:
            pass

    # Check if source is a local file
    source_path = Path(cfg.source)
    if source_path.exists() and source_path.is_file():
        provenance = "local_file"

    return RegistryStatus(
        source=cfg.source,
        ref=cfg.ref,
        cache_path=cache_path,
        cache_exists=cache_exists,
        cache_mtime=cache_mtime,
        tool_count=tool_count,
        provenance=provenance,
    )
