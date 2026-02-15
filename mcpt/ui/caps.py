"""Capability definitions and risk scoring."""

from typing import Dict, Tuple

# Risk Levels
RISK_NONE = 0
RISK_LOW = 1
RISK_MED = 2
RISK_HIGH = 3
RISK_CRITICAL = 4

# Capability Badge definitions
# Map: capability_key -> (Display Label, Risk Level)
CAP_DEFINITIONS: Dict[str, Tuple[str, int]] = {
    # Network
    "network": ("NET", RISK_HIGH),
    "http": ("HTTP", RISK_MED),
    
    # Filesystem
    "filesystem_read": ("READ", RISK_MED),
    "filesystem_write": ("WRITE", RISK_HIGH),
    "filesystem": ("FS", RISK_HIGH),
    
    # System
    "exec": ("EXEC", RISK_CRITICAL),
    "subprocess": ("PROC", RISK_CRITICAL),
    "shell": ("SHELL", RISK_CRITICAL),
    "env": ("ENV", RISK_MED),
    "clipboard": ("CLIP", RISK_LOW),
    
    # AI/Model
    "model_context": ("CTX", RISK_LOW),
    "sampling": ("SMPL", RISK_LOW),
    
    # Browser
    "browser": ("WEB", RISK_HIGH),
    "screenshot": ("SCRN", RISK_MED),
}

def get_cap_info(capability: str) -> Tuple[str, int]:
    """Get display label and risk level for a capability.
    
    Returns:
        (label, risk_level) - defaults to (CAP, RISK_MED) for unknown caps.
    """
    normalized = capability.lower().replace("-", "_")
    
    # Direct match
    if normalized in CAP_DEFINITIONS:
        return CAP_DEFINITIONS[normalized]
        
    # Prefix matching (e.g. "network.outbound" -> "network")
    for key, val in CAP_DEFINITIONS.items():
        if normalized.startswith(key):
            return val
            
    return (normalized[:4].upper(), RISK_MED)

def get_risk_color(level: int) -> str:
    """Get color for risk level."""
    if level >= RISK_CRITICAL:
        return "bold red"
    if level >= RISK_HIGH:
        return "red"
    if level >= RISK_MED:
        return "yellow"
    if level >= RISK_LOW:
        return "blue"
    return "dim white"
