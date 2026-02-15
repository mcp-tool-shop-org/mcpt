"""Rendering components for tool display."""

from typing import Any, List, Optional

from rich.table import Table
from rich.text import Text
from rich.style import Style
from rich.console import RenderableType
from rich.box import SIMPLE

from .sigil import get_sigil
from .style import format_risk_badge
from .trust import (
    get_trust_tier,
    get_tier_style,
    get_tier_symbol,
    TIER_NEUTRAL,
    TIER_TRUSTED,
    TIER_VERIFIED,
)
from .caps import get_cap_info, get_risk_color
from .risk import (
    calculate_risk_score,
    get_risk_tier,
    get_risk_style,
    RISK_LEVEL_LOW,
    RISK_LEVEL_MED,
    RISK_LEVEL_HIGH,
    RISK_LEVEL_EXTREME,
)

def render_tool_line(
    tool: dict[str, Any], 
    show_caps: bool = True,
    plain: bool = False,
    sigil_style: str = "unicode",
    force_dim: bool = False,
) -> RenderableType:
    """Render a single tool as a styled grid line.
    
    Format: [Sigil] ID [Trust] [Risk] Description
    """
    tool_id = tool.get("id", "unknown")
    desc = tool.get("description", "") or ""
    bundles = tool.get("_bundles")
    tier = get_trust_tier(tool, bundles)
    caps = tool.get("capabilities", [])
    grants = tool.get("_grants", [])
    
    # Calculate Risk Score
    risk_score = calculate_risk_score(caps)
    risk_level = get_risk_tier(risk_score)
    
    row_items = []
    
    if force_dim:
        # Simplified/Dimmed rendering for deprecated/other status
        if not plain and sigil_style != "off":
             glyph, _ = get_sigil(tool_id)
             row_items.append(Text(f" {glyph} ", style="dim"))
        
        # ID (strikethrough or dim)
        row_items.append(Text(f" {tool_id}", style="dim strike" if not plain else ""))
        
        # Trust (skip or dim)
        if not plain:
            t_sym = get_tier_symbol(tier)
            row_items.append(Text(f" {t_sym} ", style="dim"))
            
        # Risk (skip)
        if not plain and show_caps:
            row_items.append(Text(" - ", style="dim"))

        # Description
        row_items.append(Text(f" {desc}", style="dim italic" if not plain else "", no_wrap=True, overflow="ellipsis"))
        
        grid = Table.grid(padding=(0, 0))
        grid.add_row(*row_items)
        return grid

    # 1. Sigil with Risk Aura
    if not plain and sigil_style != "off":
        glyph, id_color = get_sigil(tool_id)
        t_style_obj = get_tier_style(tier)
        
        # Determine Sigil Color
        sigil_color = id_color
        marker = ""
        
        # Trusted/Verified: Keep trust color, use marker for risk
        if tier in (TIER_TRUSTED, TIER_VERIFIED):
            if t_style_obj.color:
                sigil_color = t_style_obj.color.name
            
            # Risk Marker
            if risk_level == RISK_LEVEL_EXTREME:
                marker = "‼"
            elif risk_level == RISK_LEVEL_HIGH:
                marker = "▲"
            elif risk_level == RISK_LEVEL_MED:
                marker = "·"
                
        # Neutral/Experimental: Allow risk to tint
        else:
            if risk_level == RISK_LEVEL_EXTREME:
                sigil_color = "red"
            elif risk_level == RISK_LEVEL_HIGH:
                sigil_color = "orange1" # Amber
            # elif risk_level == RISK_LEVEL_MED:
            #     sigil_color = "gold1" # Subtle amber
            elif t_style_obj.color:
                sigil_color = t_style_obj.color.name

        bg_style = f"bold white on {sigil_color}"

        if sigil_style == "ascii":
            import hashlib
            h = hashlib.sha256(tool_id.encode()).hexdigest()[:4].upper()
            sigil = Text(f"[{h}]", style=f"bold {sigil_color}")
        else:
            # Glyph + Marker
            # Using 1 char glyph, marker might push width?
            # Standard glyphs are single width usually.
            content = f" {glyph}"
            if marker:
                content += marker
            else:
                content += " "
            sigil = Text(content, style=bg_style)
            
        row_items.append(sigil)
    
    # 2. ID
    name_style = "bold"
    if not plain and tier != TIER_NEUTRAL:
        t_style_obj = get_tier_style(tier)
        if t_style_obj.color:
             name_style = f"bold {t_style_obj.color.name}"
             
    name = Text(f" {tool_id}", style=name_style if not plain else "")
    row_items.append(name)
    
    # 3. Trust
    if not plain:
        t_sym = get_tier_symbol(tier)
        t_style_obj = get_tier_style(tier)
        trust = Text(f" {t_sym} ", style=t_style_obj)
        row_items.append(trust)
    
    # 4. Capability Badges (Semantic)
    if show_caps and caps:
        badges = []
        for c in caps:
            lbl, r = get_cap_info(c)
            if plain:
                if c in grants:
                    badges.append(lbl)
                else:
                    badges.append(f"{lbl}!")
            else:
                if c in grants:
                    # Granted: use risk color
                    color = get_risk_color(r)
                    badges.append(Text(lbl, style=f"bold {color}"))
                else:
                    # Missing: Bright Red !
                    badges.append(Text(f"{lbl}!", style="bold red reverse"))
        
        if badges:
            # Join with space
            res = Text(" ")
            for i, b in enumerate(badges):
                if i > 0:
                    res.append(" ")
                if isinstance(b, str):
                    res.append(b)
                else:
                    res.append(b)
            row_items.append(res)
    elif not plain:
         pass
         # Maybe placeholder if no caps but space reserved?
         # "Safe" badge?
         
    # 5. Description
    row_items.append(Text(f" {desc}", style="dim" if not plain else "", no_wrap=True, overflow="ellipsis"))
    
    # Layout
    grid = Table.grid(padding=(0, 0))
    grid.add_row(*row_items)
    
    return grid

    
    # 5. Description
    row_items.append(Text(desc, style="dim" if not plain else "", no_wrap=True, overflow="ellipsis"))
    
    # Layout
    grid = Table.grid(padding=(0, 1))
    grid.add_row(*row_items)
    
    return grid


def render_tool_header(tool: dict[str, Any]) -> RenderableType:
    """Render a prominent header for tool details."""
    tool_id = tool.get("id", "unknown")
    name = tool.get("name", "")
    desc = tool.get("description", "")
    bundles = tool.get("_bundles")
    tier = get_trust_tier(tool, bundles)
    
    glyph, id_color = get_sigil(tool_id)
    t_style_obj = get_tier_style(tier)
    t_sym = get_tier_symbol(tier)
    
    if tier == TIER_NEUTRAL or not t_style_obj.color:
        sigil_color = id_color
    else:
        sigil_color = t_style_obj.color.name
        
    grid = Table.grid(padding=(0, 1))
    grid.add_row(
        Text(f" {glyph} ", style=f"bold white on {sigil_color}"),
        Text(f" {tool_id} ", style=f"bold white reverse {sigil_color}"),
        Text(f" {t_sym} ", style=t_style_obj),
        Text(tier.upper(), style=t_style_obj)
    )
    
    full_desc = desc
    if name and name != tool_id:
        full_desc = f"{name} • {desc}"

    if full_desc:
        grid.add_row("", Text(full_desc, style="dim"), "", "")
        
    return grid

def render_search_table(
    tools: List[dict[str, Any]], 
    title: str = "Search Results",
    plain: bool = False,
    show_badges: bool = True,
    sigil_style: str = "unicode",
    show_explain: bool = False,
) -> Table:
    # Plain mode: minimalist table, no colors/emoji if avoidable by Rich (but we control content).
    # However, Rich's Console(no_color=True) handles color stripping best.
    # Here we just avoid adding the complex columns like Sigil if plain is strictly "no glyphs".
    # The prompt says: "--plain (no color, no glyph)".

    if plain:
        box_style = None
        header_style = ""
    else:
        box_style = SIMPLE
        header_style = "bold cyan"

    table = Table(title=title, box=box_style, header_style=header_style, show_edge=False, pad_edge=False)
    
    # Columns
    if not plain and sigil_style != "off":
        table.add_column("Sigil", justify="center", width=4 if sigil_style == "unicode" else 6)
    
    table.add_column("ID", style="bold" if not plain else "")
    
    if not plain:
        table.add_column("Trust", justify="center", width=3)
        if show_badges:
            table.add_column("Risk", justify="center")
            
    table.add_column("Description")
    
    for tool in tools:
        tool_id = tool.get("id", "unknown")
        bundles = tool.get("_bundles")
        tier = get_trust_tier(tool, bundles)
        desc = tool.get("description", "")
        tags = tool.get("tags", [])
        
        row_items = []
        
        # 1. Sigil
        if not plain and sigil_style != "off":
            glyph, id_color = get_sigil(tool_id)
            t_style_obj = get_tier_style(tier)

            if tier == TIER_NEUTRAL or not t_style_obj.color:
                sigil_color = id_color
                # Default style
                style_def = f"bold white on {sigil_color}"
            else:
                sigil_color = t_style_obj.color.name
                style_def = f"bold white on {sigil_color}"

            if sigil_style == "ascii":
                # Deterministic short hash [ABCD]
                import hashlib
                h = hashlib.sha256(tool_id.encode()).hexdigest()[:4].upper()
                sigil = Text(f"[{h}]", style=f"bold {sigil_color}")
            else:
                sigil = Text(f"{glyph}", style=style_def)
            row_items.append(sigil)
        
        # 2. ID
        id_style = "bold"
        if not plain and tier != TIER_NEUTRAL:
             t_style_obj = get_tier_style(tier)
             if t_style_obj.color:
                  id_style = f"bold {t_style_obj.color.name}"
        
        row_items.append(Text(tool_id, style=id_style if not plain else ""))
        
        # 3. Trust
        if not plain:
             t_sym = get_tier_symbol(tier)
             t_style_obj = get_tier_style(tier)
             row_items.append(Text(t_sym, style=t_style_obj))
        
        # 4. Risk
        if not plain and show_badges:
            caps = tool.get("capabilities", [])
            max_risk = 0
            for c in caps:
                lbl, r = get_cap_info(c)
                max_risk = max(max_risk, r)
            
            if max_risk > 0:
                risk = format_risk_badge(max_risk)
            else:
                risk = Text("-", style="dim")
            row_items.append(risk)

        # 5. Description
        desc_text = Text(desc, style="dim" if not plain else "")
        if tags and not plain:
             desc_text.append(f" ({', '.join(tags)})", style="dim cyan")
        elif tags:
             desc_text.append(f" ({', '.join(tags)})")
             
        # Explanation (if present)
        score = tool.get("_score")
        reasons = tool.get("_reasons")
        if show_explain and score is not None and reasons:
            s_text = f"\nScore: {score:.2f} | {', '.join(reasons)}"
            desc_text.append(s_text, style="dim magenta" if not plain else "")
             
        row_items.append(desc_text)
            
        table.add_row(*row_items)
        
    return table


