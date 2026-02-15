"""Deterministic sigil generation for tools."""

import hashlib
from typing import Tuple
from functools import lru_cache

# High-compatibility Unicode glyphs
GLYPHS = [
    "⬢", "◆", "●", "■", "▲", "▼", "◀", "▶", 
    "★", "✦", "✴", "✷", "✸", "✹", "✺", "✻"
]

# Base colors (avoiding danger execution red for identity)
COLORS = [
    "cyan", 
    "blue", 
    "green", 
    "magenta", 
    "yellow",
    "bright_cyan",
    "bright_blue",
    "bright_magenta",
    "bright_green",
]

@lru_cache(maxsize=1024)
def get_sigil(tool_id: str) -> Tuple[str, str]:
    """Get the deterministic (glyph, color) pair for a tool ID.
    
    Args:
        tool_id: The unique identifier of the tool.
        
    Returns:
        A tuple of (glyph_char, color_name).
    """
    # Use SHA256 for stability across platforms/runs
    h = hashlib.sha256(tool_id.encode("utf-8")).digest()
    
    # Use different bytes for glyph and color to maximize variance
    glyph_idx = h[0] % len(GLYPHS)
    color_idx = h[1] % len(COLORS)
    
    return GLYPHS[glyph_idx], COLORS[color_idx]
