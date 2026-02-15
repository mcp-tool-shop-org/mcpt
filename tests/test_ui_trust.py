"""Tests for trust tier logic and styling."""

from mcpt.ui.trust import (
    get_trust_tier,
    get_tier_style,
    TIER_TRUSTED,
    TIER_VERIFIED,
    TIER_NEUTRAL,
    TIER_EXPERIMENTAL,
    TIER_DEPRECATED,
)

def test_trust_tier_precedence_deprecated():
    """Ensure deprecated overrides everything."""
    tool = {
        "id": "foo",
        "deprecated": True,
        "maturity": "stable",
        "_bundles": ["core"]
    }
    tier = get_trust_tier(tool, ["core"])
    assert tier == TIER_DEPRECATED

def test_trust_tier_precedence_maturity():
    """Ensure maturity overrides bundle."""
    tool = {
        "id": "foo",
        "maturity": "stable",
        "_bundles": ["evaluation"]
    }
    tier = get_trust_tier(tool, ["evaluation"])
    assert tier == TIER_TRUSTED
    
    tool["maturity"] = "experimental"
    # Even if in core bundle (unlikely), explicit experimental marking should win?
    # Our logic says: 2. Maturity -> 3. Bundle.
    # So if maturity=experimental, returns EXPERIMENTAL.
    tier = get_trust_tier(tool, ["core"])
    assert tier == TIER_EXPERIMENTAL

def test_trust_tier_bundle_defaults():
    """Ensure bundles provide defaults when maturity missing."""
    tool = {"id": "foo"}
    
    assert get_trust_tier(tool, ["core"]) == TIER_TRUSTED
    assert get_trust_tier(tool, ["ops"]) == TIER_VERIFIED
    assert get_trust_tier(tool, ["evaluation"]) == TIER_EXPERIMENTAL
    assert get_trust_tier(tool, ["random"]) == TIER_NEUTRAL

def test_trust_tier_default():
    """Ensure default is neutral."""
    tool = {"id": "foo"}
    assert get_trust_tier(tool, []) == TIER_NEUTRAL

def test_tier_styles():
    """Ensure styles are defined."""
    style = get_tier_style(TIER_TRUSTED)
    assert style.color.name in ("gold1", "yellow")
    assert style.bold is True
    
    style = get_tier_style(TIER_DEPRECATED)
    assert style.strike is True
