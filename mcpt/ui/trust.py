"""Trust model and tier definitions."""

from typing import Any, Dict, List, Optional
from rich.style import Style

# Trust Tiers
TIER_TRUSTED = "trusted"         # Core/Stable - Gold/Green
TIER_VERIFIED = "verified"       # Ops/Verified - Green
TIER_NEUTRAL = "neutral"         # Standard - Default Color
TIER_EXPERIMENTAL = "experimental" # Alpha/Eval - Dim/Purple
TIER_DEPRECATED = "deprecated"   # Deprecated - Dim/Red/Strike

# Configuration
# Can be overridden by user config
TIER_STYLES = {
    TIER_TRUSTED: Style(color="gold1", bold=True),
    TIER_VERIFIED: Style(color="green"),
    TIER_NEUTRAL: Style(color="white"),  # Will usually fallback to sigil color
    TIER_EXPERIMENTAL: Style(color="magenta", dim=True),
    TIER_DEPRECATED: Style(color="red", dim=True, strike=True),
}

TIER_SYMBOLS = {
    TIER_TRUSTED: "🛡️",
    TIER_VERIFIED: "✓",
    TIER_NEUTRAL: "•",
    TIER_EXPERIMENTAL: "🧪",
    TIER_DEPRECATED: "🚫",
}

def get_trust_tier(
    tool: Dict[str, Any], 
    bundles: Optional[List[str]] = None
) -> str:
    """Determine trust tier for a tool based on metadata precedence.
    
    Precedence:
    1. Deprecated
    2. Maturity (stable > beta > alpha)
    3. Bundle membership (core > ops > agents > evaluation)
    4. Default (NEUTRAL)
    """
    # 1. Deprecated
    if tool.get("deprecated"):
        return TIER_DEPRECATED
        
    # 2. Maturity
    # Maturity isn't standard in registry v1 yet, but we prepare for it
    maturity = tool.get("maturity", "").lower()
    if maturity in ("stable", "ga", "production"):
        return TIER_TRUSTED
    if maturity in ("beta",):
        return TIER_NEUTRAL
    if maturity in ("alpha", "experimental", "dev"):
        return TIER_EXPERIMENTAL
        
    # 3. Bundle Membership
    # Bundles are passed in, or we could look them up if we had context
    # Assuming `bundles` list contains names of bundles this tool is in
    if bundles:
        if "core" in bundles:
            return TIER_TRUSTED
        if "ops" in bundles:
            return TIER_VERIFIED
        if "evaluation" in bundles:
            return TIER_EXPERIMENTAL
            
    # 4. Default
    return TIER_NEUTRAL

def get_tier_style(tier: str) -> Style:
    """Get the Rich Style for a given tier."""
    return TIER_STYLES.get(tier, Style())

def get_tier_symbol(tier: str) -> str:
    """Get the symbol for a given tier."""
    return TIER_SYMBOLS.get(tier, "?")
