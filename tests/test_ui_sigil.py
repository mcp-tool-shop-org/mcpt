"""Tests for UI components and sigil generation."""

from mcpt.ui.sigil import get_sigil
from mcpt.ui.caps import get_cap_info, RISK_HIGH, RISK_MED, RISK_CRITICAL
from mcpt.ui.style import format_risk_badge, get_trust_style, TIER_OFFICIAL

def test_sigil_determinism():
    """Ensure sigils are stable for the same input."""
    s1, c1 = get_sigil("tool-a")
    s2, c2 = get_sigil("tool-a")
    assert s1 == s2
    assert c1 == c2
    
def test_sigil_collision_resistance():
    """Ensure different inputs yield different results (probabilistically)."""
    results = set()
    for i in range(20):
        res = get_sigil(f"tool-{i}")
        results.add(res)
    # With 16 glyphs * 9 colors = 144 combos, 20 tools should result in >10 unique sigils
    assert len(results) > 10
    
def test_risk_badges():
    """Ensure risk badges are formatted correctly."""
    badge = format_risk_badge(RISK_HIGH)
    s = str(badge)
    style = str(badge.style)
    # Rich text string content can be accessed via .plain usually, but str works too.
    assert "HIGH" in s
    assert "red" in style

def test_trust_styles():
    """Ensure trust tiers return correct symbols."""
    sym, color = get_trust_style(TIER_OFFICIAL)
    assert sym == "🛡️"
    assert color == "blue"
    
    sym, color = get_trust_style("unknown-garbage")
    assert sym == "?"
    assert "yellow" in color

def test_cap_definitions():
    """Ensure capabilities are mapped correctly."""
    # Known capability
    label, risk = get_cap_info("network")
    assert label == "NET"
    assert risk == RISK_HIGH
    
    # Unknown capability defaults to medium
    label, risk = get_cap_info("unknown-cap")
    assert risk == 2 # RISK_MED
    
    # Prefix matching logic verification
    # "filesystem.read" normalizes to "filesystem_read" which matches exact entry if present
    # But wait, caps.py helper: `normalized = capability.lower().replace("-", "_")`
    # "filesystem.read" -> "filesystem.read". No replacement of dot.
    # Then `startswith`: "filesystem.read" starts with "filesystem"? Yes.
    # So "filesystem" -> ("FS", HIGH).
    
    label, risk = get_cap_info("filesystem")
    assert label == "FS"
    assert risk == RISK_HIGH
