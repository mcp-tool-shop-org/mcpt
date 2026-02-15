"""MCPT CLI - CLI for discovering and running MCP Tool Shop tools."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Annotated, List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mcpt import __version__
from mcpt.registry import (
    RegistryConfig,
    get_registry,
    get_registry_status,
    get_tool,
    search_tools,
    load_cached_artifact,
    get_featured,
    FeaturedData,
    Section,
    Collection,
)
from mcpt.workspace import (
    MCP_YAML_FILENAME,
    add_tool as workspace_add_tool,
    read_config,
    remove_tool as workspace_remove_tool,
    write_default,
    grant_capability,
    revoke_capability,
    get_grants,
    write_lock_record,
    read_lock,
)
from mcpt.runner import generate_run_plan, stub_run

app = typer.Typer(
    help="CLI for discovering and running MCP Tool Shop tools.",
    no_args_is_help=True,
)


def fuzzy_match_tools(query: str, limit: int = 5) -> list[dict]:
    """Find tools with similar names using simple fuzzy matching."""
    from difflib import SequenceMatcher

    registry = get_registry()
    tools = registry.get("tools", [])
    query_lower = query.lower()

    scored = []
    for tool in tools:
        tool_id = tool.get("id", "")
        # Score based on: substring match, sequence similarity, starts-with
        score = 0
        if query_lower in tool_id.lower():
            score += 0.5
        if tool_id.lower().startswith(query_lower):
            score += 0.3
        score += SequenceMatcher(None, query_lower, tool_id.lower()).ratio() * 0.5
        if score > 0.2:
            scored.append((score, tool))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored[:limit]]


console = Console()


# ============================================================================
# Global options
# ============================================================================


def version_callback(value: bool) -> None:
    if value:
        console.print(f"mcpt {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = False,
) -> None:
    """MCPT CLI - Discover and run MCP Tool Shop tools."""
    pass


# ============================================================================
# Registry commands
# ============================================================================


from mcpt.ui.render import render_search_table, render_tool_header
from mcpt.ui.risk import calculate_risk_score, get_risk_tier, RISK_LEVEL_EXTREME, RISK_LEVEL_HIGH, RISK_LEVEL_MED, RISK_LEVEL_LOW
from mcpt.ui.caps import get_cap_info, get_risk_color, RISK_CRITICAL, RISK_HIGH, RISK_MED, RISK_LOW, RISK_NONE
from mcpt.workspace import (
    MCP_YAML_FILENAME,
    add_tool as workspace_add_tool,
    read_config,
    remove_tool as workspace_remove_tool,
    write_default,
    grant_capability,
    revoke_capability,
    get_grants,
    write_lock_record,
    read_lock,
    get_ui_config,
)
from mcpt.registry.client import get_bundle_membership

def render_tools(
    tools: list[dict[str, Any]], 
    title: str = "Search Results", 
    deprecated: bool = False,
    plain: bool = False,
    no_badges: bool = False,
    sigil_style: str = "unicode",
    explain: bool = False,
) -> None:
    """Helper to render tools using unified UI."""
    
    # Enrich tools with bundle info for trust calculation
    # We do this here to keep it centralized for all lists/searches
    bundle_map = get_bundle_membership()
    for tool in tools:
        if "id" in tool and tool["id"] in bundle_map:
            tool["_bundles"] = bundle_map[tool["id"]]

    console.print(
        render_search_table(
            tools, 
            title=title, 
            plain=plain, 
            show_badges=not no_badges,
            sigil_style=sigil_style,
            show_explain=explain
        )
    )
    console.print()

@app.command("list")
def list_tools(
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
    refresh: Annotated[bool, typer.Option("--refresh", help="Force refresh from remote")] = False,
    bundle: Annotated[Optional[str], typer.Option("--bundle", help="Filter by bundle")] = None,
    tag: Annotated[Optional[str], typer.Option("--tag", help="Filter by tag")] = None,
    collection: Annotated[Optional[str], typer.Option("--collection", "-c", help="Filter by collection")] = None,
    featured: Annotated[bool, typer.Option("--featured", help="Show featured tools only")] = False,
    include_deprecated: Annotated[bool, typer.Option("--include-deprecated", help="Show deprecated tools")] = False,
    plain: Annotated[bool, typer.Option("--plain", help="No color, no glyphs")] = False,
    no_badges: Annotated[bool, typer.Option("--no-badges", help="Hide risk badges")] = False,
    force_rich: Annotated[bool, typer.Option("--force-rich", help="Force rich output even if non-TTY")] = False,
) -> None:
    """List all available tools in the registry."""
    import os
    
    # Auto-detect plain mode
    if not plain:
        if "NO_COLOR" in os.environ:
            plain = True
        elif not sys.stdout.isatty() and not force_rich:
            plain = True

    try:
        registry = get_registry(force_refresh=refresh)
    except Exception as e:
        console.print(f"[red]Error fetching registry:[/red] {e}")
        raise typer.Exit(1)

    tools = registry.get("tools", [])

    # Filter deprecated
    if not include_deprecated:
        tools = [t for t in tools if not t.get("deprecated")]

    # Filter by tag
    if tag:
        tools = [t for t in tools if tag.lower() in [x.lower() for x in t.get("tags", [])]]

    # Filter by bundle
    if bundle:
        cfg = RegistryConfig()
        index = load_cached_artifact(cfg, "registry.index.json")
        if index and "bundles" in index and bundle in index["bundles"]:
            allowed = set(index["bundles"][bundle])
            tools = [t for t in tools if t.get("id") in allowed]
        else:
            if index:
                 console.print(f"[yellow]Bundle '{bundle}' not found.[/yellow]")
            else:
                 console.print("[yellow]Bundle index not available.[/yellow]")
            tools = []

    # Filter by featured / collection
    if featured or collection:
        cfg = RegistryConfig()
        f_data = get_featured(cfg)
        if f_data:
            allowed = set()
            if featured:
                allowed.update(f_data.featured)
                # Should featured flag strictly mean "tools in featured list" or "tools in any featured section"?
                # Prompt says: "Show featured tools only" -- usually means the top level featured list.
                # However, usually featured includes whatever is in 'sections' too.
                # Let's stick to f_data.featured for now as that's the canonical 'featured' list.
                
                # Also include "Tools of the Week" if section exists?
                for s in f_data.sections:
                    if "week" in s.title.lower() or "featured" in s.title.lower():
                        allowed.update(s.tool_ids)

            if collection:
                if collection in f_data.collections:
                    allowed.update(f_data.collections[collection].tool_ids)
                else:
                    console.print(f"[yellow]Collection '{collection}' not found.[/yellow]")
                    tools = []
            
            # If both flags set, intersection or union?
            # Typer typically implies cumulative filters narrow results (intersection), 
            # BUT here we built an 'allowed' set which is additive.
            # If 'tools' are filtered by 'allowed', it means tool MUST be in 'allowed'.
            # So if usage is `list --featured --collection X`, user probably wants tools that are EITHER featured OR in collection X?
            # Or tools that are in BOTH?
            # Given the flags populate 'allowed', and we filter by 'allowed', it behaves as Union of criteria?
            # Wait, allowed is initialized empty.
            # If --featured, we add featured tools.
            # If --collection, we add collection tools.
            # Then we filter tools to only those in allowed.
            # This is Union logic (Show me featured stuff AND collection stuff).
            
            if allowed:
                tools = [t for t in tools if t.get("id") in allowed]
            elif (featured or collection): 
                # Filters were requested but nothing matched or data missing
                tools = []
        else:
            if featured or collection:
                 console.print("[yellow]Featured data not available.[/yellow]")
                 tools = []

    if json_output:
        # Strip internal fields
        clean_tools = [{k: v for k, v in t.items() if not k.startswith("_")} for t in tools]
        console.print(json.dumps(clean_tools, indent=2))
        return

    if not tools:
        console.print("[dim]No tools found.[/dim]")
        return

    # 2.4 Config plumbing
    # Check mcp.yaml for ui settings
    path = Path.cwd() / MCP_YAML_FILENAME
    ui_cfg = get_ui_config(path)
    
    # Sigil config: unicode|ascii|off
    sigil_style = ui_cfg.get("sigil", "unicode")
    # Badges config: on|off
    badges_setting = ui_cfg.get("badges", "on")
    
    # CLI Overrides
    # If user says --plain, force plain mode (no color/glyphs)
    # If user says --no-badges, force no badges
    # But plain implies no badges? render_search_table logic: if plain, show_badges=False? No, code says:
    # "if not plain and show_badges:"
    # So plain implies hidden badges.
    
    # Combining logic:
    # effective_plain = plain
    # effective_no_badges = no_badges or (badges_setting == "off")
    
    render_tools(
        tools, 
        title="MCP Tools", 
        deprecated=include_deprecated,
        plain=plain, 
        no_badges=no_badges or (badges_setting == "off"),
        sigil_style=sigil_style
    )



@app.command("featured")
def featured(
    collection: Annotated[Optional[str], typer.Option("--collection", "-c", help="Show only a specific collection")] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
    plain: Annotated[bool, typer.Option("--plain", help="No color, no glyphs")] = False,
    refresh: Annotated[bool, typer.Option("--refresh", help="Force refresh registry")] = False,
    list_collections: Annotated[bool, typer.Option("--list", "--list-collections", help="List available collections")] = False,
    force_rich: Annotated[bool, typer.Option("--force-rich", help="Force rich output even if non-TTY")] = False,
) -> None:
    """Browse featured tools and collections."""
    from mcpt.ui.featured import render_featured_view
    from dataclasses import asdict
    import os

    # Auto-detect plain mode
    if not plain:
        if "NO_COLOR" in os.environ:
            plain = True
        elif not sys.stdout.isatty() and not force_rich:
            plain = True

    try:
        cfg = RegistryConfig()
        tools_map = {}
        
        # Load registry for tool details
        try:
            full_registry = get_registry(cfg, force_refresh=refresh)
            tools_map = {t["id"]: t for t in full_registry.get("tools", [])}
        except Exception as e:
            console.print(f"[yellow]Warning: Could not fetch registry: {e}[/yellow]")

        data = get_featured(cfg)
        if not data:
            console.print("[yellow]No featured content available.[/yellow]")
            raise typer.Exit(1)

        # --list mode
        if list_collections:
            if json_output:
                res = [{"slug": c.slug, "title": c.title, "description": c.description} for c in data.collections.values()]
                console.print(json.dumps(res, indent=2))
            else:
                console.print(Panel("[bold]Available Collections[/bold]", style="blue"))
                for c in data.collections.values():
                    desc = f" - {c.description}" if c.description else ""
                    console.print(f" • [cyan bold]{c.slug}[/cyan bold]: {c.title}[italic]{desc}[/italic]")
            return

        # Prepare view data
        if collection:
            if collection not in data.collections:
                console.print(f"[red]Collection '{collection}' not found.[/red]")
                raise typer.Exit(1)
            
            # Show ONLY this collection as a section
            target = data.collections[collection]
            view_data = FeaturedData(
                featured=[], 
                collections={},
                sections=[
                    Section(
                        title=target.title,
                        tool_ids=target.tool_ids,
                        description=target.description
                    )
                ]
            )
        else:
            view_data = data

        if json_output:
            out = asdict(view_data)
            console.print(json.dumps(out, indent=2))
            return

        # Render
        # Context for sigils
        path = Path.cwd() / MCP_YAML_FILENAME
        ui_cfg = get_ui_config(path)
        sigil_style = ui_cfg.get("sigil", "unicode")

        console.print(render_featured_view(
            view_data, 
            tools_map, 
            plain=plain,
            sigil_style=sigil_style
        ))

    except Exception as e:
        console.print(f"[red]Error displaying featured content:[/red] {e}")
        # if debug: raise e
        raise typer.Exit(1)


@app.command()
def info(
    tool_id: Annotated[str, typer.Argument(help="Tool ID to get info for")],
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show detailed information about a tool."""
    tool = get_tool(tool_id)

    if tool is None:
        console.print(f"[red]Tool not found:[/red] {tool_id}")
        console.print("[dim]Stale registry? Try: mcpt list --refresh[/dim]")
        raise typer.Exit(1)

    if json_output:
        console.print(json.dumps(tool, indent=2))
        return

    console.print()
    # 2.3 Show big header with sigil
    console.print(render_tool_header(tool))
    console.print()

    if tool.get("deprecated"):
        reason = tool.get("deprecation_reason", "No reason provided")
        console.print(Panel(f"[bold red]DEPRECATED[/bold red]\n{reason}", style="red"))
        console.print()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="dim", width=15)
    table.add_column("Value")
    
    # Try to load bundle info from index

    cfg = RegistryConfig()
    try:
        index = load_cached_artifact(cfg, "registry.index.json")
        bundles = []
        if index and "bundles" in index:
            for b_name, b_tools in index["bundles"].items():
                if tool_id in b_tools:
                    bundles.append(b_name)
        if bundles:
             tool["_bundles"] = bundles
    except Exception:
        pass

    # Basic info
    table.add_row("Description", tool.get("description", ""))
    if tool.get("deprecated"):
        table.add_row("Status", "[red]Deprecated[/red]")
        
    # Lock status
    path = Path.cwd() / MCP_YAML_FILENAME
    lock_data = read_lock(path)
    installed = lock_data.get("tools", {}).get(tool_id)
    if installed:
        table.add_row("Installed Ref", installed.get("ref", "unknown"))
        table.add_row("Installed At", installed.get("installed_at", "unknown"))
    
    if "_bundles" in tool:
        table.add_row("Bundles", ", ".join(tool["_bundles"]))

    # Risk Analysis
    caps = tool.get("capabilities", [])
    risk_score = calculate_risk_score(caps)
    risk_level = get_risk_tier(risk_score)
    
    risk_style = "dim"
    if risk_level == RISK_LEVEL_EXTREME:
        risk_style = "bold red"
    elif risk_level == RISK_LEVEL_HIGH:
        risk_style = "bold orange1"
    elif risk_level == RISK_LEVEL_MED:
        risk_style = "gold1"
        
    table.add_row("Risk Score", f"[{risk_style}]{risk_level.upper()} ({risk_score})[/{risk_style}]")

    # Capabilities
    path = Path.cwd() / MCP_YAML_FILENAME
    granted = get_grants(path, tool_id) if path.exists() else []
    
    if caps:
        caps_lines = []
        for cap in caps:
            lbl, r_level = get_cap_info(cap)
            r_color = get_risk_color(r_level)
            
            # Status icon
            status_icon = "[red]![/red]"
            status_text = "Missing Grant"
            
            if cap in granted:
                status_icon = "[green]✓[/green]"
                status_text = "Granted"
            
            # Line format: ✓ [NET] network (High Risk)
            # Use columns or rich formatting
            
            risk_badge = ""
            if r_level >= RISK_CRITICAL:
                risk_badge = "[bold red reverse] CRITICAL [/bold red reverse]"
            elif r_level >= RISK_HIGH:
                risk_badge = "[orange1]High Risk[/orange1]"
            elif r_level >= RISK_MED:
                risk_badge = "[gold1]Med Risk[/gold1]"
                
            line = f"{status_icon} [bold {r_color}]{lbl}[/bold {r_color}] {cap} {risk_badge}"
            caps_lines.append(line)
        
        # Check granted but not requested (unusual but possible)
        for cap in granted:
            if cap not in caps:
                caps_lines.append(f"[yellow]? {cap} (granted extra)[/yellow]")
            
        table.add_row("Capabilities", "\n".join(caps_lines))
    else:
        table.add_row("Capabilities", "[dim]None requested[/dim]")

    # Install Info
    table.add_row("Install Command", f"[bold cyan]mcpt install {tool_id}[/bold cyan]")
    table.add_row("Repository", tool.get("repo", ""))
    table.add_row("Install Type", tool.get("install", {}).get("type", ""))
    table.add_row("Git URL", tool.get("install", {}).get("url", ""))
    table.add_row("Default Ref", tool.get("install", {}).get("default_ref", ""))
    table.add_row("Tags", ", ".join(tool.get("tags", [])))
    table.add_row("Safe Run", str(tool.get("defaults", {}).get("safe_run", True)))

    console.print(table)
    console.print()


@app.command()
def icons(
    plain: Annotated[bool, typer.Option("--plain", help="Print the legend in pure text")] = False,
) -> None:
    """Show the visual legend and icons cheat sheet."""
    from mcpt.ui.legend import render_legend
    console.print(render_legend(plain=plain))


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search query")] = "",
    bundle: Annotated[
        Optional[str],
        typer.Option("--bundle", help="Filter by bundle (e.g., core, productivity)"),
    ] = None,
    tag: Annotated[
        Optional[str],
        typer.Option("--tag", help="Filter by tag (e.g., agents)"),
    ] = None,
    collection: Annotated[
        Optional[str],
        typer.Option("--collection", "-c", help="Filter by collection (e.g., starter)"),
    ] = None,
    featured: Annotated[
        bool,
        typer.Option("--featured", help="Search featured tools only"),
    ] = False,
    explain: Annotated[
        bool,
        typer.Option("--explain", help="Show match reasons and scores"),
    ] = False,
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
    plain: Annotated[bool, typer.Option("--plain", help="No color, no glyphs")] = False,
    no_badges: Annotated[bool, typer.Option("--no-badges", help="Hide risk badges")] = False,
    force_rich: Annotated[bool, typer.Option("--force-rich", help="Force rich output even if non-TTY")] = False,
) -> None:
    """Search for tools in the registry with ranking."""
    import os
    if not plain:
        if "NO_COLOR" in os.environ:
            plain = True
        elif not sys.stdout.isatty() and not force_rich:
            plain = True
            
    # Pre-filter for collections/featured logic
    # search_tools doesn't support featured/collection filters natively, 
    # but we can filter the result set or pre-filter if we pass a allow-list.
    # search_tools signature: (query, bundle, tag) -> list[dict]
    
    tools = search_tools(query, bundle=bundle, tag=tag)

    # Apply featured filters
    if featured or collection:
        cfg = RegistryConfig()
        f_data = get_featured(cfg)
        if f_data:
            allowed = set()
            if featured:
                allowed.update(f_data.featured)
                for s in f_data.sections:
                    if "week" in s.title.lower() or "featured" in s.title.lower():
                        allowed.update(s.tool_ids)
            
            if collection:
                if collection in f_data.collections:
                    allowed.update(f_data.collections[collection].tool_ids)
                else:
                    console.print(f"[yellow]Collection '{collection}' not found.[/yellow]")
                    tools = [] # Force empty results
            
            if allowed:
                tools = [t for t in tools if t.get("id") in allowed]
            elif (featured or collection):
                # Filter requested but no criteria matched
                tools = []
        else:
            tools = []
            console.print("[dim]Featured data unavailable -- skipping filter results[/dim]")

    if json_output:
        # Strip internal fields unless specifically requested, but for now output clean tools
        clean_tools = [{k: v for k, v in t.items() if not k.startswith("_")} for t in tools]
        console.print(json.dumps(clean_tools, indent=2))
        return

    if not tools:
        console.print(f"[dim]No tools found matching:[/dim] {query}")
        console.print("[dim]Stale registry? Try: mcpt list --refresh[/dim]")
        return

    # Config (same as list command)
    path = Path.cwd() / MCP_YAML_FILENAME
    ui_cfg = get_ui_config(path)
    sigil_style = ui_cfg.get("sigil", "unicode")
    badges_setting = ui_cfg.get("badges", "on")

    render_tools(
        tools,
        title=f"Search Results: {query}" if query else "Search Results",
        plain=plain,
        no_badges=no_badges or (badges_setting == "off"),
        sigil_style=sigil_style,
        explain=explain
    )



@app.command()
def bundles(
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """List available tool bundles."""
    cfg = RegistryConfig()
    try:
        index = load_cached_artifact(cfg, "registry.index.json")
    except Exception:
        index = None

    if not index or "bundles" not in index:
        console.print("[yellow]Bundle index not available.[/yellow] Try 'mcpt list --refresh'")
        return

    bundle_data = index["bundles"]
    
    if json_output:
        console.print(json.dumps(bundle_data, indent=2))
        return

    table = Table(title="Tool Bundles")
    table.add_column("Bundle", style="bold cyan")
    table.add_column("Tools Preview", style="green")
    table.add_column("Count")

    for name, tool_ids in sorted(bundle_data.items()):
        preview = ", ".join(tool_ids[:3])
        if len(tool_ids) > 3:
            preview += f", +{len(tool_ids)-3} more"
        
        table.add_row(name, preview, str(len(tool_ids)))

    console.print(table)


@app.command()
def facets(
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show registry facets and statistics."""
    cfg = RegistryConfig()
    try:
        report = load_cached_artifact(cfg, "registry.report.json")
    except Exception:
        report = None
    
    if not report:
        console.print("[yellow]Registry report not available.[/yellow] Try 'mcpt list --refresh'")
        return

    if json_output:
        console.print(json.dumps(report, indent=2))
        return
    
    console.print(Panel(f"[bold]Registry Facets[/bold] (generated {report.get('generated_at', 'unknown')})"))
    
    # Stats
    stats = report.get("stats", {})
    if stats:
        console.print("\n[bold]General Statistics[/bold]")
        for k, v in stats.items():
            console.print(f"  - {k}: [cyan]{v}[/cyan]")

    # Top Tags
    if "tags" in report:
        console.print("\n[bold]Top Tags[/bold]")
        for tag, count in list(report.get("tags", {}).items())[:10]:
            console.print(f"  - {tag}: [dim]{count}[/dim]")
            
    # Bundle Sizes
    if "bundle_sizes" in report:
        console.print("\n[bold]Bundle Sizes[/bold]")
        for bundle, size in report.get("bundle_sizes", {}).items():
            console.print(f"  - {bundle}: [dim]{size}[/dim]")


# ============================================================================
# Workspace commands
# ============================================================================


@app.command()
def init(
    path: Annotated[
        Optional[Path],
        typer.Argument(help="Directory to initialize (default: current directory)"),
    ] = None,
    force: Annotated[bool, typer.Option("--force", "-f", help="Overwrite existing mcp.yaml")] = False,
    registry_ref: Annotated[
        Optional[str],
        typer.Option("--registry-ref", help="Registry git ref (default: v0.3.0)"),
    ] = None,
) -> None:
    """Initialize a new MCP workspace with mcp.yaml."""
    from mcpt.registry.client import DEFAULT_REF

    if path is None:
        path = Path.cwd()

    config_path = path / MCP_YAML_FILENAME

    if config_path.exists() and not force:
        console.print(f"[yellow]{MCP_YAML_FILENAME} already exists.[/yellow] Use --force to overwrite.")
        raise typer.Exit(1)

    path.mkdir(parents=True, exist_ok=True)
    write_default(config_path, registry_ref=registry_ref or DEFAULT_REF)
    console.print(f"[green]Created[/green] {config_path}")


@app.command()
def add(
    tool_id: Annotated[str, typer.Argument(help="Tool ID to add")],
    ref: Annotated[Optional[str], typer.Option("--ref", help="Git ref to use")] = None,
    path: Annotated[
        Optional[Path],
        typer.Option("--path", "-p", help="Path to mcp.yaml"),
    ] = None,
    allow_deprecated: Annotated[bool, typer.Option("--allow-deprecated", help="Allow adding deprecated tools")] = False,
) -> None:
    """Add a tool to the workspace configuration."""
    if path is None:
        path = Path.cwd() / MCP_YAML_FILENAME

    if not path.exists():
        console.print(f"[red]{MCP_YAML_FILENAME} not found.[/red] Run 'mcpt init' first.")
        raise typer.Exit(1)

    # Verify tool exists in registry
    tool = get_tool(tool_id)
    if tool is None:
        console.print(f"[red]Tool not found in registry:[/red] {tool_id}")
        # Show fuzzy matches
        similar = fuzzy_match_tools(tool_id)
        if similar:
            console.print("[dim]Did you mean:[/dim]")
            for t in similar:
                console.print(f"  [cyan]{t.get('id')}[/cyan] - {t.get('name', '')}")
        console.print("[dim]Stale registry? Try: mcpt list --refresh[/dim]")
        raise typer.Exit(1)

    # Check deprecation
    if tool.get("deprecated"):
        console.print(f"[bold red]Warning: {tool_id} is deprecated[/bold red]")
        if tool.get("deprecation_reason"):
            console.print(f"[dim]{tool.get('deprecation_reason')}[/dim]")
        
        if not allow_deprecated:
            if not typer.confirm("Do you want to continue adding this tool?"):
                 console.print("[red]Aborted.[/red]")
                 raise typer.Exit(1)
                 
    # Warn about capabilities
    needed = tool.get("capabilities", [])
    if needed:
        console.print(f"[yellow]Note: {tool_id} requires the following capabilities to run:[/yellow]")
        for cap in needed:
            console.print(f"  - {cap}")
        console.print("You can grant these later with 'mcpt grant'")

    if workspace_add_tool(path, tool_id, ref):
        console.print(f"[green]Added[/green] {tool_id} to {path}")
        # Show capability hints if tool has side effects
        defaults = tool.get("defaults", {})
        if not defaults.get("safe_run", True):
            console.print("[dim]Note: This tool has side effects. Check its documentation for capability env vars.[/dim]")
    else:
        console.print(f"[yellow]{tool_id} already in workspace.[/yellow]")


@app.command()
def remove(
    tool_id: Annotated[str, typer.Argument(help="Tool ID to remove")],
    path: Annotated[
        Optional[Path],
        typer.Option("--path", "-p", help="Path to mcp.yaml"),
    ] = None,
) -> None:
    """Remove a tool from the workspace configuration."""
    if path is None:
        path = Path.cwd() / MCP_YAML_FILENAME

    if not path.exists():
        console.print(f"[red]{MCP_YAML_FILENAME} not found.[/red]")
        raise typer.Exit(1)

    if workspace_remove_tool(path, tool_id):
        console.print(f"[green]Removed[/green] {tool_id} from {path}")
    else:
        console.print(f"[yellow]{tool_id} not found in workspace.[/yellow]")


@app.command()
def grant(
    tool_id: Annotated[str, typer.Argument(help="Tool ID")],
    capability: Annotated[str, typer.Argument(help="Capability to grant (e.g. network, filesystem_write)")],
    path: Annotated[
        Optional[Path],
        typer.Option("--path", "-p", help="Path to mcp.yaml"),
    ] = None,
) -> None:
    """Grant a capability to a tool."""
    if path is None:
        path = Path.cwd() / MCP_YAML_FILENAME
    
    if not path.exists():
        console.print(f"[red]{MCP_YAML_FILENAME} not found.[/red]")
        raise typer.Exit(1)
        
    if grant_capability(path, tool_id, capability):
        console.print(f"[green]Granted[/green] {capability} to {tool_id}")
    else:
        console.print(f"[red]Failed:[/red] Tool {tool_id} not found in workspace.")
        raise typer.Exit(1)


@app.command()
def revoke(
    tool_id: Annotated[str, typer.Argument(help="Tool ID")],
    capability: Annotated[str, typer.Argument(help="Capability to revoke")],
    path: Annotated[
        Optional[Path],
        typer.Option("--path", "-p", help="Path to mcp.yaml"),
    ] = None,
) -> None:
    """Revoke a capability from a tool."""
    if path is None:
        path = Path.cwd() / MCP_YAML_FILENAME
    
    if not path.exists():
        console.print(f"[red]{MCP_YAML_FILENAME} not found.[/red]")
        raise typer.Exit(1)
        
    if revoke_capability(path, tool_id, capability):
        console.print(f"[green]Revoked[/green] {capability} from {tool_id}")
    else:
        console.print(f"[yellow]No change:[/yellow] Capability not found or tool missing.")


# ============================================================================
# Install command
# ============================================================================


@app.command()
def install(
    tool_id: Annotated[str, typer.Argument(help="Tool ID to install")],
    ref: Annotated[Optional[str], typer.Option("--ref", help="Git ref to install")] = None,
    venv: Annotated[
        Optional[Path],
        typer.Option("--venv", help="Virtual environment to install into"),
    ] = None,
    allow_deprecated: Annotated[bool, typer.Option("--allow-deprecated", help="Allow installing deprecated tools")] = False,
) -> None:
    """Install a tool via git into a virtual environment."""
    tool = get_tool(tool_id)

    if tool is None:
        console.print(f"[red]Tool not found:[/red] {tool_id}")
        raise typer.Exit(1)
        
    # Check deprecation
    if tool.get("deprecated"):
        console.print(f"[bold red]Warning: {tool_id} is deprecated[/bold red]")
        if tool.get("deprecation_reason"):
            console.print(f"[dim]{tool.get('deprecation_reason')}[/dim]")
        
        if not allow_deprecated:
            if not typer.confirm("Do you want to continue installing this tool?"):
                 console.print("[red]Aborted.[/red]")
                 raise typer.Exit(1)

    install_info = tool.get("install", {})
    if install_info.get("type") != "git":
        console.print(f"[red]Unsupported install type:[/red] {install_info.get('type')}")
        raise typer.Exit(1)

    git_url = install_info.get("url", "")
    git_ref = ref or install_info.get("default_ref", "main")

    # Determine pip executable
    if venv:
        pip_path = venv / "Scripts" / "pip.exe" if sys.platform == "win32" else venv / "bin" / "pip"
        if not pip_path.exists():
            console.print(f"[red]pip not found in venv:[/red] {pip_path}")
            raise typer.Exit(1)
        pip_cmd = str(pip_path)
    else:
        pip_cmd = "pip"

    # Install via pip git+url@ref
    install_url = f"git+{git_url}@{git_ref}"
    console.print(f"[dim]Installing {tool_id} from {install_url}...[/dim]")

    try:
        result = subprocess.run(
            [pip_cmd, "install", install_url],
            capture_output=True,
            text=True,
            check=True,
        )
        console.print(f"[green]Installed[/green] {tool_id}")
        if result.stdout:
            console.print(result.stdout)
            
        # Write lock record
        from datetime import datetime, timezone
        record = {
            "source": f"git+{git_url}",
            "ref": git_ref,
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "install_type": "git",
        }
        # Assuming we are in a workspace if we are installing?
        # The prompt says "mcpt install via git into a virtual environment".
        # It doesn't strictly require a workspace file existing for 'install' depending on how it's used,
        # but 'mcpt install' usually implies adding to local capacity.
        # But 'add' is for workspace config. 'install' is for environments.
        # However, to store the lock, we need a workspace.
        # Let's assume current directory.
        path = Path.cwd() / MCP_YAML_FILENAME
        write_lock_record(path, tool_id, record)
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Installation failed:[/red]")
        if e.stderr:
            console.print(e.stderr)
        raise typer.Exit(1)


# ============================================================================
# Run command
# ============================================================================


@app.command()
def run(
    tool_id: Annotated[str, typer.Argument(help="Tool ID to run")],
    args: Annotated[Optional[List[str]], typer.Argument(help="Arguments to pass to the tool")] = None,
    mode: Annotated[str, typer.Option("--mode", help="Execution mode: stub, restricted, real")] = "stub",
    real: Annotated[bool, typer.Option("--real", help="[Deprecated] Alias for --mode restricted")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Print plan but do not execute")] = False,
) -> None:
    """Run a tool (stub by default)."""
    # Backwards compatibility for --real
    if real and mode == "stub":
        mode = "restricted"

    tool = get_tool(tool_id)

    if tool is None:
        console.print(f"[red]Tool not found:[/red] {tool_id}")
        raise typer.Exit(1)
        
    # Execution checks for non-stub modes
    if mode in ["restricted", "real"]:
        path = Path.cwd() / MCP_YAML_FILENAME
        
        # 1. Capability Checks
        if path.exists():
             needed = tool.get("capabilities", [])
             granted = get_grants(path, tool_id)
             missing = [c for c in needed if c not in granted]
             
             if missing:
                 console.print(f"[bold red]Execution Blocked ({mode} mode)[/bold red]")
                 console.print(f"Tool {tool_id} requires the following capabilities that are not granted:")
                 for m in missing:
                     console.print(f"  - {m}")
                 console.print(f"\nUse 'mcpt grant {tool_id} <capability>' to allow, or run in stub mode.")
                 raise typer.Exit(1)
        else:
             needed = tool.get("capabilities", [])
             if needed:
                 console.print(f"[bold red]Execution Blocked ({mode} mode)[/bold red]")
                 console.print(f"Tool {tool_id} requires capabilities: {', '.join(needed)}")
                 console.print(f"No workspace configuration found ({MCP_YAML_FILENAME}). Run 'mcpt init' first.")
                 raise typer.Exit(1)

        # 2. Lock/Install Checks (Commit 3.2 logic reused/implied)
        # Ideally we check if installed.
        lock_data = read_lock(path) if path.exists() else {"tools": {}}
        if tool_id not in lock_data["tools"]:
             console.print(f"[yellow]Warning: Tool {tool_id} does not appear to be installed (no lock record).[/yellow]")
             console.print("Execution may fail if dependencies are missing. Run 'mcpt install' to fix.")

    plan = generate_run_plan(tool, args)
    
    if dry_run:
        console.print(Panel(f"[bold yellow]DRY RUN[/bold yellow] - Mode: {mode}", title="Execution Plan"))
        console.print(json.dumps(plan, indent=2))
        return

    if mode == "stub":
        stub_run(tool_id, plan)
        return

    # Real execution
    console.print(f"[bold green]Executing[/bold green] {tool_id} (Mode: {mode})...")
    console.print("[yellow]Real execution not yet implemented in Python runner.[/yellow]")
    console.print("[dim]Tool would be executed with the following plan:[/dim]")
    console.print(json.dumps(plan, indent=2))
    
    if mode == "restricted":
        console.print("[dim]Note: Restricted mode would enforce runtime sandboxing here.[/dim]")


# ============================================================================
# Utility commands
# ============================================================================


@app.command()
def registry(
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Show detailed registry status and provenance."""
    status = get_registry_status()
    dist = status.cache_path.parent / "dist"
    
    artifacts = {
        "index": (dist / "registry.index.json").exists(),
        "capabilities": (dist / "capabilities.json").exists(),
        "report": (dist / "registry.report.json").exists(),
        "llms": (dist / "registry.llms.txt").exists(),
    }
    
    if json_output:
        out = {
            "source": status.source,
            "ref": status.ref,
            "cache_path": str(status.cache_path),
            "artifacts": artifacts,
            "tool_count": status.tool_count,
            "last_fetched": status.cache_mtime.isoformat() if status.cache_mtime else None,
        }
        console.print(json.dumps(out, indent=2))
        return

    console.print(Panel(f"[bold cyan]MCP Tool Registry[/bold cyan]", subtitle=f"Ref: {status.ref}"))
    console.print(f"  [bold]Source:[/bold] {status.source}")
    console.print(f"  [bold]Tools:[/bold]  {status.tool_count}")
    if status.cache_mtime:
        console.print(f"  [bold]Cached:[/bold] {status.cache_mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        console.print("  [bold]Cached:[/bold] [yellow]Never[/yellow]")
        
    console.print("\n[bold]Artifacts[/bold]")
    for art, exists in artifacts.items():
        state = "[green]✓[/green]" if exists else "[dim]missing[/dim]"
        console.print(f"  {state} {art}")


@app.command()
def check(
    tool_id: Annotated[str, typer.Argument(help="Tool ID to check")],
    json_output: Annotated[bool, typer.Option("--json", help="Output as JSON")] = False,
) -> None:
    """Pre-flight check for tool execution."""
    tool = get_tool(tool_id)
    if not tool:
        if json_output:
             console.print(json.dumps({"error": "Tool not found"}, indent=2))
        else:
             console.print(f"[red]Tool not found:[/red] {tool_id}")
        raise typer.Exit(1)
        
    path = Path.cwd() / MCP_YAML_FILENAME
    workspace_exists = path.exists()
    
    # Check 1: Registry Metadata
    checks = {
        "registry": True,
        "workspace": workspace_exists,
        "capabilities": True, # valid until proven invalid
        "grants": [],
        "missing_grants": [],
    }
    
    # Check 2: Capabilities
    needed = tool.get("capabilities", [])
    if needed and workspace_exists:
        granted = get_grants(path, tool_id)
        checks["grants"] = granted
        missing = [c for c in needed if c not in granted]
        checks["missing_grants"] = missing
        if missing:
            checks["capabilities"] = False
    elif needed and not workspace_exists:
         checks["capabilities"] = False
         checks["missing_grants"] = needed

    # Check 3: Install Status
    path_lock = path / MCP_YAML_FILENAME # path arg passed to check is usually tool_id? No, check uses CWD.
    # check(tool_id) doesn't take path arg.
    # path in check() is 'Path.cwd() / MCP_YAML_FILENAME'
    lock_data = read_lock(path)
    installed_record = lock_data.get("tools", {}).get(tool_id)
    
    config = read_config(path) if workspace_exists else {}
    tools_list = config.get("tools", [])
    is_added = False
    for t in tools_list:
        if isinstance(t, str) and t == tool_id:
            is_added = True
        elif isinstance(t, dict) and t.get("id") == tool_id:
            is_added = True
    
    checks["added_to_workspace"] = is_added
    checks["installed"] = bool(installed_record)
    checks["install_details"] = installed_record
    
    if json_output:
        console.print(json.dumps(checks, indent=2))
        return
        
    console.print(Panel(f"[bold cyan]Preflight Check: {tool_id}[/bold cyan]"))
    
    # Registry
    console.print("[bold]Registry Metadata:[/bold] [green]OK[/green]")
    
    # Workspace
    if checks["workspace"]:
        console.print("[bold]Workspace Config:[/bold] [green]Found[/green]")
    else:
        console.print("[bold]Workspace Config:[/bold] [red]Missing[/red] (Run 'mcpt init')")
        
    # Added
    if checks["added_to_workspace"]:
        console.print("[bold]Added to Workspace:[/bold] [green]Yes[/green]")
    else:
        console.print("[bold]Added to Workspace:[/bold] [yellow]No[/yellow] (Run 'mcpt add')")

    # Installed
    if checks["installed"]:
        console.print(f"[bold]Installed:[/bold] [green]Yes[/green] ({checks['install_details'].get('ref', 'unknown')})")
    else:
        console.print("[bold]Installed:[/bold] [yellow]No[/yellow] (Run 'mcpt install')")
        
    # Risk Profile
    caps = tool.get("capabilities", [])
    risk_score = calculate_risk_score(caps)
    risk_level = get_risk_tier(risk_score)
    r_style = "green"
    if risk_level == RISK_LEVEL_HIGH:
        r_style = "bold orange1"
    elif risk_level == RISK_LEVEL_EXTREME:
        r_style = "bold red"
        
    console.print(f"[bold]Risk Profile:[/bold] [{r_style}]{risk_level.upper()} ({risk_score})[/{r_style}]")

    # Capabilities
    if not needed:
        console.print("[bold]Capabilities:[/bold] [dim]None required[/dim]")
    else:
        if checks["capabilities"]:
            console.print("[bold]Capabilities:[/bold] [green]All granted[/green]")
        else:
            console.print("[bold]Capabilities:[/bold] [red]Missing Grants[/red]")
            for m in checks["missing_grants"]:
                lbl, r_lvl = get_cap_info(m)
                badge = ""
                if r_lvl >= RISK_CRITICAL:
                     badge = f" [bold red reverse] {lbl}! [/bold red reverse]"
                elif r_lvl >= RISK_HIGH:
                     badge = f" [bold red]({lbl}: HIGH RISK)[/bold red]"
                elif r_lvl >= RISK_MED:
                     badge = f" [yellow]({lbl}: Med Risk)[/yellow]"

                console.print(f"  - [red]{m}[/red]{badge} -> Run 'mcpt grant {tool_id} {m}'")

    # Overall Status
    ready = checks["registry"] and checks["workspace"] and checks["capabilities"]
    console.print()
    if ready:
        console.print("[bold green]READY TO RUN[/bold green]")
    else:
        console.print("[bold red]CHECKS FAILED[/bold red]")
        raise typer.Exit(1)


@app.command()
def doctor() -> None:
    """Check MCPT CLI configuration and connectivity."""
    console.print("[bold]MCPT Doctor[/bold]")
    console.print()

    # Check Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    console.print(f"[dim]Python:[/dim] {py_version}")

    # Registry provenance
    console.print()
    console.print("[bold]Registry Status[/bold]")
    status = get_registry_status()
    console.print(f"  [dim]Source:[/dim] {status.source}")
    console.print(f"  [dim]Ref:[/dim] {status.ref}")
    if status.ref == "main":
        console.print("  [yellow]Tip:[/yellow] Pin to a tagged release (e.g., v0.3.0) for reproducibility.")
    console.print(f"  [dim]Cache:[/dim] {status.cache_path}")

    if status.cache_exists:
        mtime_str = status.cache_mtime.strftime("%Y-%m-%d %H:%M:%S") if status.cache_mtime else "unknown"
        console.print(f"  [dim]Last fetched:[/dim] {mtime_str}")
        console.print(f"  [dim]Cached tools:[/dim] {status.tool_count}")

        # Provenance indicator
        if status.provenance == "cache":
            console.print(f"  [yellow]Provenance:[/yellow] Loaded from cache (use --refresh to update)")
        elif status.provenance == "local_file":
            console.print(f"  [yellow]Provenance:[/yellow] Local file (not from remote)")
    else:
        console.print(f"  [dim]Cache:[/dim] not found")

    # Check remote connectivity
    console.print()
    console.print("[dim]Checking remote connectivity...[/dim]")
    try:
        registry = get_registry(force_refresh=True)
        tool_count = len(registry.get("tools", []))
        console.print(f"[green]Remote OK[/green] - {tool_count} tools fetched")
    except Exception as e:
        console.print(f"[red]Remote error:[/red] {e}")
        if status.cache_exists:
            console.print(f"[yellow]Using cached registry ({status.tool_count} tools)[/yellow]")

    # Check for mcp.yaml in current directory
    console.print()
    config_path = Path.cwd() / MCP_YAML_FILENAME
    workspace_exists = config_path.exists()
    workspace_tools = 0
    workspace_ref = None

    if workspace_exists:
        try:
            config = read_config(config_path)
            workspace_tools = len(config.get("tools", []))
            workspace_ref = config.get("registry", {}).get("ref")
            console.print(f"[green]Workspace OK[/green] - {workspace_tools} tools configured")
        except Exception as e:
            console.print(f"[yellow]Workspace config error:[/yellow] {e}")
    else:
        console.print(f"[dim]No {MCP_YAML_FILENAME} in current directory[/dim]")

    # Next steps (max 3 bullets based on current state)
    console.print()
    console.print("[bold]Next Steps[/bold]")
    next_steps = []

    if not workspace_exists:
        next_steps.append("Run [cyan]mcpt init[/cyan] to create a workspace")
    elif workspace_tools == 0:
        next_steps.append("Run [cyan]mcpt add <tool-id>[/cyan] to add a tool")

    if workspace_ref == "main":
        next_steps.append("Edit mcp.yaml to pin [cyan]ref: v0.3.0[/cyan] for reproducibility")

    if not status.cache_exists:
        next_steps.append("Run [cyan]mcpt list --refresh[/cyan] to fetch the registry")

    if not next_steps:
        next_steps.append("[green]All good![/green] Run [cyan]mcpt list[/cyan] to explore tools")

    for step in next_steps[:3]:
        console.print(f"  • {step}")

    console.print()
    console.print("[green]Doctor complete.[/green]")


if __name__ == "__main__":
    app()
