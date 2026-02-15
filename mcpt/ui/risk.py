"""Risk scoring and tiering logic."""

from typing import List
from rich.style import Style

from .caps import get_cap_info, RISK_NONE, RISK_LOW, RISK_MED, RISK_HIGH, RISK_CRITICAL

# Risk Tiers
RISK_LEVEL_LOW = "low"
RISK_LEVEL_MED = "medium"
RISK_LEVEL_HIGH = "high"
RISK_LEVEL_EXTREME = "extreme"

# Risk Thresholds (Score based)
THRESHOLD_MED = 1
THRESHOLD_HIGH = 5
THRESHOLD_EXTREME = 10

# Styles
RISK_STYLES = {
    RISK_LEVEL_LOW: Style(),
    RISK_LEVEL_MED: Style(color="gold1"), # Dim amber
    RISK_LEVEL_HIGH: Style(color="orange1", bold=True), # Amber
    RISK_LEVEL_EXTREME: Style(color="red", bold=True), # Red
}

def calculate_risk_score(capabilities: List[str]) -> int:
    """Calculate aggregate risk score for a list of capabilities."""
    total_score = 0
    for cap in capabilities:
        _, level = get_cap_info(cap)
        # Weight the levels slightly to make Critical caps really pop
        # None=0, Low=1, Med=2, High=4, Crit=8
        if level <= RISK_LOW:
            score = level
        elif level == RISK_MED:
            score = 2
        elif level == RISK_HIGH:
            score = 4
        else: # CRITICAL
            score = 8
        total_score += score
    return total_score

def get_risk_tier(score: int) -> str:
    """Get the risk tier for a given score."""
    if score >= THRESHOLD_EXTREME:
        return RISK_LEVEL_EXTREME
    if score >= THRESHOLD_HIGH:
        return RISK_LEVEL_HIGH
    if score >= THRESHOLD_MED:
        return RISK_LEVEL_MED
    return RISK_LEVEL_LOW

def get_risk_style(tier: str) -> Style:
    """Get style for risk tier."""
    return RISK_STYLES.get(tier, Style())
