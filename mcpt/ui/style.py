"""Styling policies for tool trust and risk visualization."""

from rich.text import Text
from .caps import get_risk_color, RISK_CRITICAL, RISK_HIGH, RISK_MED, RISK_LOW

# Trust Tiers
TIER_OFFICIAL = "official"
TIER_VERIFIED = "verified"
TIER_COMMUNITY = "community"
TIER_UNKNOWN = "unknown"

def get_trust_style(tier: str | None) -> tuple[str, str]:
    """Get symbol and color for a trust tier.
    
    Returns:
        (symbol, color)
    """
    t = (tier or "").lower()
    if t == TIER_OFFICIAL:
        return ("🛡️", "blue")  # Shield for official
    if t == TIER_VERIFIED:
        return ("✓", "green")  # Check for verified
    if t == TIER_COMMUNITY:
        return ("•", "dim white")  # Dot for community
    return ("?", "dim yellow")  # Question mark for unknown

def format_risk_badge(level: int) -> Text:
    """Format a risk level as a badge."""
    color = get_risk_color(level)
    
    if level >= RISK_CRITICAL:
        label = "CRITICAL"
    elif level >= RISK_HIGH:
        label = "HIGH"
    elif level >= RISK_MED:
        label = "MED"
    elif level >= RISK_LOW:
        label = "LOW"
    else:
        label = "SAFE"
        
    # Badges are inverse (white text on color bg)
    return Text(f" {label} ", style=f"bold white on {color}")
