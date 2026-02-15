"""Featured view renderer."""

from typing import Any

from rich.console import RenderableType, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich import box

from mcpt.registry.featured import FeaturedData
from mcpt.ui.render import render_tool_line


def render_featured_view(
    data: FeaturedData,
    tools_by_id: dict[str, dict[str, Any]],
    plain: bool = False,
    sigil_style: str = "unicode",
) -> RenderableType:
    """Render the featured view with sections and collections."""
    
    parts: list[RenderableType] = []

    # 1. Sections (e.g., Tools of the Week)
    for section in data.sections:
        parts.append(
            render_section(
                title=section.title,
                tool_ids=section.tool_ids,
                description=section.description,
                tools_by_id=tools_by_id,
                plain=plain,
                sigil_style=sigil_style,
                highlight=True,
            )
        )
        parts.append(Text(""))  # Spacer

    # 2. Collections
    for slug, collection in data.collections.items():
        # Format title with slug for easy copying
        # Using a distinct styling for the slug
        display_title = f"{collection.title} [dim]({slug})[/dim]"
        
        parts.append(
            render_section(
                title=display_title,
                tool_ids=collection.tool_ids,
                description=collection.description,
                tools_by_id=tools_by_id,
                plain=plain,
                sigil_style=sigil_style,
                highlight=False,
            )
        )
        parts.append(Text(""))

    return Group(*parts)


def render_section(
    title: str,
    tool_ids: list[str],
    description: str | None,
    tools_by_id: dict[str, dict[str, Any]],
    plain: bool,
    sigil_style: str,
    highlight: bool = False,
) -> RenderableType:
    """Render a single section of tools."""
    
    # Filter valid tools
    active_tools = []
    deprecated_tools = []
    
    for tid in tool_ids:
        if tid in tools_by_id:
            tool = tools_by_id[tid]
            if tool.get("deprecated"):
                deprecated_tools.append(tool)
            else:
                active_tools.append(tool)
    
    if not active_tools and not deprecated_tools:
        return Text("")

    # Create table for tools
    table = Table(
        show_header=False, 
        box=None if plain else box.SIMPLE, 
        expand=True,
        pad_edge=False,
        padding=(0, 1)
    )
    
    table.add_column("Tool", ratio=1)
    
    for tool in active_tools:
        line = render_tool_line(tool, plain=plain, sigil_style=sigil_style)
        table.add_row(line)
        
    if deprecated_tools:
        if active_tools:
            # Add subtle separator
            table.add_row(Text("Deprecated", style="dim italic"))
            
        for tool in deprecated_tools:
            line = render_tool_line(tool, plain=plain, sigil_style=sigil_style, force_dim=True)
            table.add_row(line)

    # Wrap in Panel?
    if plain:
        # Plain text
        header = Text(title.upper(), style="bold underline")
        if description:
            header.append(f"\n{description}", style="italic")
        return Group(header, table)
    else:
        # Rich Panel
        border_style = "blue" if highlight else "dim"
        return Panel(
            table,
            title=f"[bold]{title}[/bold]",
            subtitle=description if description else None,
            subtitle_align="left",
            border_style=border_style,
            box=box.ROUNDED if highlight else box.SQUARE,
            padding=(1, 2),
        )
