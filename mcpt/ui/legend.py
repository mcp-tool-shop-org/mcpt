"""Legend and visual cheat sheet rendering."""

from rich.console import Console, RenderableType
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.layout import Layout
from rich import box

from .trust import (
    TIER_TRUSTED, TIER_VERIFIED, TIER_NEUTRAL, TIER_EXPERIMENTAL, TIER_DEPRECATED,
    TIER_STYLES, TIER_SYMBOLS
)
from .risk import (
    RISK_LEVEL_LOW, RISK_LEVEL_MED, RISK_LEVEL_HIGH, RISK_LEVEL_EXTREME,
    RISK_STYLES
)
from .caps import get_risk_color, RISK_CRITICAL, RISK_HIGH, RISK_MED, RISK_LOW
from .render import render_tool_line

def render_legend(plain: bool = False) -> RenderableType:
    """Render the visual language cheat sheet."""
    
    # 1. Trust Tiers
    trust_table = Table(title="Trust Tiers", box=box.SIMPLE, padding=(0,1), show_edge=False)
    trust_table.add_column("Symbol", justify="center")
    trust_table.add_column("Tier")
    trust_table.add_column("Description", style="dim")
    
    tiers = [
        (TIER_TRUSTED, "Official, Stable, Highest Standard"),
        (TIER_VERIFIED, "Validated Partner/Ops Tool"),
        (TIER_NEUTRAL, "Standard Community Tool"),
        (TIER_EXPERIMENTAL, "Early Evaluation / Alpha"),
        (TIER_DEPRECATED, "No longer supported"),
    ]
    
    for tier, desc in tiers:
        sym = TIER_SYMBOLS[tier]
        style = TIER_STYLES[tier]
        trust_table.add_row(
            Text(sym, style=style),
            Text(tier.upper(), style=style),
            desc
        )

    # 2. Risk Markers (Aura)
    risk_table = Table(title="Risk Markers & Aura", box=box.SIMPLE, padding=(0,1), show_edge=False)
    risk_table.add_column("Marker", justify="center")
    risk_table.add_column("Risk Level")
    risk_table.add_column("Meaning", style="dim")

    risk_table.add_row(" ", "LOW", "Benign operations (e.g. Clipboard)")
    risk_table.add_row("·", "MEDIUM", "Read-only system access")
    risk_table.add_row("▲", "HIGH", "File editing, uncontrolled network")
    risk_table.add_row("‼", "EXTREME", "Code execution, shell access")
    
    # 3. Badges
    badge_table = Table(title="Capability Badges", box=box.SIMPLE, padding=(0,1), show_edge=False)
    badge_table.add_column("Badge", justify="right")
    badge_table.add_column("State")
    badge_table.add_column("Context", style="dim")
    
    # Examples
    badge_table.add_row(
        Text("NET", style=f"bold {get_risk_color(RISK_HIGH)}"),
        "[green]Granted[/green]",
        "Capability is actively allowed"
    )
    badge_table.add_row(
        Text("EXEC!", style="bold red reverse"),
        "[red]Missing[/red]",
        "Requires explicit grant to run"
    )
    badge_table.add_row(
        Text("CLIP", style=f"bold {get_risk_color(RISK_LOW)}"),
        "Granted (Low Risk)",
        "Low risk caps are often auto-granted"
    )

    # 4. Examples
    example_tools = [
        {
            "id": "fetch",
            "description": "Fetch URLs from the web",
            "maturity": "stable", # Trusted
            "capabilities": ["network"], # High risk -> Triangle
            "_bundles": ["core"],
            "_grants": ["network"]
        },
        {
            "id": "shell-tool",
            "description": "Run shell commands",
            "capabilities": ["shell"], # Critical -> Bangs
            "_bundles": [], # Neutral
            "_grants": [] # Missing
        },
        {
            "id": "eval-agent",
            "description": "Experimental agent loop",
            "maturity": "experimental",
            "capabilities": ["filesystem_write"],
            "_bundles": [],
            "_grants": ["filesystem_write"]
        }
    ]
    
    examples_grid = Table.grid(padding=(0, 1))
    examples_grid.add_row(Text("Examples:", style="bold cyan"))
    for t in example_tools:
        examples_grid.add_row(render_tool_line(t, plain=plain))

    # Layout using grid
    layout = Table.grid(padding=(1, 2))
    layout.add_row(trust_table, risk_table)
    layout.add_row(badge_table, "")
    layout.add_row(Panel(examples_grid, title="Preview", border_style="dim"), "")
    
    return layout
