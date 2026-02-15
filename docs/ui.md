# Visual Identity & UI Configuration

`mcpt` features a polished terminal interface designed to provide quick visual cues about tool trust, risk, and identity.

## Visual Elements

### Sigils
Every tool has a deterministic "Sigil" — a unique glyph and color pair generated from its ID. This helps you recognize tools at a glance across different commands and sessions.

Example:
` ⬢  tool-a` (cyan)
` ▲  tool-b` (magenta)

### Trust Indicators
Tools are marked with trust tiers based on maturity and bundle membership:

- **Trusted** (🛡️ Gold): Official, stable, core tools. The highest standard.
- **Verified** (✓ Green): Validated tools from the Ops bundle or partners.
- **Experimental** (🧪 Purple): Tools in early development or evaluation.
- **Neutral** (•): Standard community tools.
- **Deprecated** (🚫 Red/Strike): Tools no longer supported.

### Risk Profile & Badges
Tools are scored based on the destructiveness of their requested capabilities.
- **Extreme** (Red): Can execute code, damage system, or exfiltrate data. (e.g. `EXEC`, `SHELL`)
- **High** (Orange): Can edit files or uncontrolled network access. (e.g. `WRITE`, `NET`)
- **Medium** (Gold): Read-only system access. (e.g. `READ`, `ENV`)
- **Low**: Benign operations. (e.g. `CLIP`)

### Risk Aura
Trust and Risk are displayed together. A **Trusted** tool will keep its Gold identity but may display a risk marker if it has dangerous capabilities:
- `⬢ ` (Gold Sigil): Trusted, Low Risk.
- `⬢·` (Gold Sigil + Dot): Trusted, Medium Risk.
- `⬢▲` (Gold Sigil + Triangle): Trusted, High Risk.
- `⬢‼` (Gold Sigil + Bangs): Trusted, Extreme Risk.

Non-trusted tools (Neutral/Experimental) will have their entire sigil tinted by the risk color (e.g., Red for Extreme Risk).

## Commands

### Visual Legend
Run `mcpt icons` to see a quick cheat sheet of all symbols, tiers, and risk markers types available in your terminal.

```bash
$ mcpt icons
```

### Listing Tools
`mcpt list` displays the registry with full visual styling.
```bash
$ mcpt list
```

### Searching
`mcpt search <query>` ranks results and shows visual indicators.
```bash
$ mcpt search "python"
```
Use `--explain` to see why a tool matched and its relevance score.

### Tool Info
`mcpt info <tool_id>` shows a detailed header with the sigil and a breakdown of requested vs granted capabilities.

## Configuration

You can customize the UI in your `mcp.yaml` (workspace) or global configuration.

```yaml
ui:
  # Sigil style: unicode (default), ascii, or off
  sigil: unicode
  
  # Badges: on (default) or off
  badges: on
  
  # Plain mode (no color/glyphs) is supported via CLI flag only currently
```

### CLI Overrides
- `--plain`: Disable all colors and glyphs (useful for CI or scripts).
- `--no-badges`: Hide risk badges.

## Examples

**Standard View:**
```
 ⬢  fetch  🛡️  NET  Fetch URLs from the web
 ▲  shell  •  EXEC  Run shell commands
```

**Plain View (`--plain`):**
```
fetch (NET) Fetch URLs from the web
shell (EXEC) Run shell commands
```

## Accessibility & Automation

### Accessibility Modes
- **Plain Mode**: Use `--plain` or set `NO_COLOR=1` env var. Removes all colors and glyphs.
- **ASCII Mode**: Set `ui.sigil: ascii` in config. Replaces glyphs with stable short hashes like `[A1B2]`.
- **Force Color**: Use `--force-rich` to enable color when piping output.

### CI / Automation Contract (UI Stability)
The visual output of `mcpt list`, `search`, and `info` is designed for human consumption and **is not a stable API**. We generally adhere to SemVer, but visual tweaks (colors, padding, glyphs) may happen in minor releases.

For automation scripts:
- **ALWAYS** use the `--json` flag.
- The JSON output structure is stable and follows the internal schema.
- Do not screen-scrape the text output.

Example:
```bash
# Bad (Fragile)
if mcpt list | grep " fetch "; then ...

# Good (Robust)
mcpt list --json | jq '.[] | select(.id=="fetch")'
```
