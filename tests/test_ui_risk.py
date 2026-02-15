"""Tests for risk scoring and rendering logic."""

from mcpt.ui.risk import (
    calculate_risk_score,
    get_risk_tier,
    RISK_LEVEL_LOW,
    RISK_LEVEL_MED,
    RISK_LEVEL_HIGH,
    RISK_LEVEL_EXTREME,
)
from mcpt.ui.render import render_tool_line

def test_risk_scoring_basics():
    # Empty
    assert calculate_risk_score([]) == 0
    assert get_risk_tier(0) == RISK_LEVEL_LOW
    
    # Low risk items
    # clipboard is low risk (level 1), score 1
    assert calculate_risk_score(["clipboard"]) == 1
    assert get_risk_tier(1) == RISK_LEVEL_MED # Threshold is >= 1
    
    # Med risk
    # filesystem_read is med risk (level 2), score 2
    assert calculate_risk_score(["filesystem_read"]) == 2
    assert get_risk_tier(2) == RISK_LEVEL_MED

def test_risk_scoring_high():
    # High risk cap
    # filesystem_write is high risk (level 3), score 4
    assert calculate_risk_score(["filesystem_write"]) == 4
    assert get_risk_tier(4) == RISK_LEVEL_MED # 4 < 5 (High Threshold)
    
    # Two high risks
    # 4 + 4 = 8 -> High tier (>=5)
    assert calculate_risk_score(["filesystem_write", "network"]) == 8
    assert get_risk_tier(8) == RISK_LEVEL_HIGH

def test_risk_scoring_extreme():
    # Critical = 8 points
    # exec is Critical
    score = calculate_risk_score(["exec"])
    assert score == 8
    assert get_risk_tier(score) == RISK_LEVEL_HIGH
    
    # Exec + Net = 8 + 4 = 12 -> Extreme (>=10)
    score = calculate_risk_score(["exec", "network"])
    assert score == 12
    assert get_risk_tier(score) == RISK_LEVEL_EXTREME

def test_render_aura_marker():
    """Smoke test for render logic with risk."""
    tool = {
        "id": "trusted-risky",
        "maturity": "stable",
        "capabilities": ["exec", "network"] # Extreme risk
    }
    
    # Should not throw
    res = render_tool_line(tool)
    assert res is not None

def test_render_caps_badges():
    """Smoke test for capability badges."""
    tool = {
        "id": "badges-test",
        "capabilities": ["network", "filesystem_read"],
        "_grants": ["network"] # One granted, one missing
    }
    
    res = render_tool_line(tool, show_caps=True)
    assert res is not None
