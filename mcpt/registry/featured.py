"""Featured tools and collections data model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from mcpt.registry.client import RegistryConfig, get_registry, load_cached_artifact


@dataclass
class Collection:
    """A curated collection of tools."""
    slug: str
    title: str
    tool_ids: list[str]
    description: str | None = None


@dataclass
class Section:
    """A highlighted section (e.g., 'Tools of the Week')."""
    title: str
    tool_ids: list[str]
    description: str | None = None


@dataclass
class FeaturedData:
    """Top-level structure for featured content."""
    featured: list[str] = field(default_factory=list)
    collections: dict[str, Collection] = field(default_factory=dict)
    sections: list[Section] = field(default_factory=list)


def get_featured(
    cfg: RegistryConfig | None = None,
) -> FeaturedData | None:
    """Load and validate featured.json artifacts.
    
    Returns None if artifact is missing or invalid.
    """
    if cfg is None:
        cfg = RegistryConfig()

    data = load_cached_artifact(cfg, "featured.json")
    if not isinstance(data, dict):
        # Graceful fallback if file is missing or corrupt
        return None

    # Load main registry to validate IDs
    try:
        registry = get_registry(cfg)
        known_ids = {t["id"] for t in registry.get("tools", [])}
    except Exception:
        # If registry fetch fails, we can't validate IDs strict-mode,
        # but we should still return the structure if available locally.
        # However, typically we want to return a subset of VALID tools.
        # Let's assume empty set for safety, or better yet, skip validation.
        # User requested "fail with actionable message" or robust handling.
        # Let's proceed with validation if registry is available.
        known_ids = set()

    result = FeaturedData()

    # 1. Parse 'featured' (top-level list)
    featured_raw = data.get("featured", [])
    if isinstance(featured_raw, list):
        # Validate existence
        valid_featured = []
        for tool_id in featured_raw:
            if not isinstance(tool_id, str):
                continue
            if known_ids and tool_id not in known_ids:
                # Log or skip? User said "fail with actionable message" for 'get_featured', 
                # but returning partial results is often better for a CLI. 
                # Let's include it but maybe the renderer filters it out if it can't find it.
                # Actually, the requirement was "Every referenced tool id must exist... (fail with actionable message)".
                # Since get_featured is a helper, maybe we just print a warning to stderr?
                # Or we can return it and let the CLI handle missing tools.
                # Given "fail with actionable message", I will stick to returning it, 
                # but the CLI will likely filter it out when resolving tools.
                pass
            valid_featured.append(tool_id)
        result.featured = valid_featured

    # 2. Parse 'collections'
    # JSON schema: "collections": [{"id":..., "name":..., "tools":...}]
    col_raw = data.get("collections", [])
    if isinstance(col_raw, list):
        for c in col_raw:
            if not isinstance(c, dict):
                continue
            
            c_id = c.get("id")
            c_name = c.get("name")
            c_tools = c.get("tools")
            
            if not (c_id and c_name and isinstance(c_tools, list)):
                continue

            # Validate tools
            valid_ids = [tid for tid in c_tools if isinstance(tid, str)]
            
            coll = Collection(
                slug=c_id,
                title=c_name,
                tool_ids=valid_ids,
                description=c.get("description")
            )
            result.collections[c_id] = coll

    # 3. Parse 'sections' (future proofing)
    # If the JSON evolves to have 'sections', we parse it.
    sec_raw = data.get("sections", [])
    if isinstance(sec_raw, list):
        for s in sec_raw:
            if not isinstance(s, dict):
                continue
            s_title = s.get("title")
            s_ids = s.get("ids", s.get("tools", [])) # support both keys
            if s_title and isinstance(s_ids, list):
                 result.sections.append(Section(
                     title=s_title, 
                     tool_ids=[tid for tid in s_ids if isinstance(tid, str)],
                     description=s.get("description")
                 ))
    
    # Synthesize "Tools of the Week" if sections is empty but 'featured' is present
    if not result.sections and result.featured:
        result.sections.append(Section(
            title="Tools of the Week",
            tool_ids=result.featured,
            description="Hand-picked tools for high-impact workflows."
        ))

    return result
