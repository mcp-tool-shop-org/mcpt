import type { SiteConfig } from '@mcptoolshop/site-theme';

export const config: SiteConfig = {
  title: 'mcpt',
  description: 'CLI for discovering and running MCP Tool Shop tools',
  logoBadge: 'MC',
  brandName: 'mcpt',
  repoUrl: 'https://github.com/mcp-tool-shop-org/mcpt',
  npmUrl: 'https://www.npmjs.com/package/@mcptoolshop/mcpt',
  footerText: 'MIT Licensed — built by <a href="https://github.com/mcp-tool-shop-org" style="color:var(--color-muted);text-decoration:underline">mcp-tool-shop-org</a>',

  hero: {
    badge: 'Open source',
    headline: 'mcpt',
    headlineAccent: 'your MCP toolkit.',
    description: 'CLI for discovering, installing, and running MCP Tool Shop tools — with trust tiers, capability grants, and workspace pinning.',
    primaryCta: { href: '#quick-start', label: 'Get started' },
    secondaryCta: { href: '#features', label: 'Learn more' },
    previews: [
      { label: 'Install', code: 'pip install mcp-select' },
      { label: 'Discover', code: 'mcpt list --refresh' },
      { label: 'Run', code: 'mcpt run file-compass' },
    ],
  },

  sections: [
    {
      kind: 'features',
      id: 'features',
      title: 'Features',
      subtitle: 'Safe-by-default tool management for MCP.',
      features: [
        { title: 'Trust Tiers', desc: 'Four-level trust system (trusted, verified, neutral, experimental) with visual risk auras so you know exactly what you\'re running.' },
        { title: 'Safe by Default', desc: 'Tools run in stub mode unless explicitly promoted. Capability grants are enforced before real execution.' },
        { title: 'Workspace Pinning', desc: 'Pin registry refs and individual tool versions in mcp.yaml for fully deterministic, reproducible builds.' },
        { title: 'Registry-First', desc: 'Official client for the mcp-tool-registry — the canonical source of truth for all MCP Tool Shop tools.' },
        { title: 'Rich TUI', desc: 'Beautiful terminal output with unicode sigils, badges, and color. Supports --plain and NO_COLOR for CI.' },
        { title: 'Dual Distribution', desc: 'Available on PyPI (mcp-select) and npm (@mcptoolshop/mcpt). One CLI, two ecosystems.' },
      ],
    },
    {
      kind: 'code-cards',
      id: 'quick-start',
      title: 'Quick Start',
      cards: [
        {
          title: 'Python (recommended)',
          code: 'pip install mcp-select\n\nmcpt list --refresh\nmcpt init\nmcpt add file-compass\nmcpt install file-compass\nmcpt run file-compass',
        },
        {
          title: 'npm wrapper',
          code: 'npx @mcptoolshop/mcpt          # one-shot\nnpm install -g @mcptoolshop/mcpt  # global\n\nmcpt list --refresh',
        },
      ],
    },
    {
      kind: 'data-table',
      id: 'commands',
      title: 'Commands',
      subtitle: 'Everything you need to discover, manage, and run tools.',
      columns: ['Command', 'Description'],
      rows: [
        ['mcpt list', 'List all available tools in the registry'],
        ['mcpt search <query>', 'Search for tools with ranked results'],
        ['mcpt info <tool-id>', 'Show detailed information about a tool'],
        ['mcpt init', 'Initialize a workspace (mcp.yaml)'],
        ['mcpt add <tool-id>', 'Add a tool to the workspace'],
        ['mcpt install <tool-id>', 'Install a tool via git + venv'],
        ['mcpt run <tool-id>', 'Run a tool (stub by default)'],
        ['mcpt grant <tool-id> <cap>', 'Grant a capability to a tool'],
        ['mcpt check <tool-id>', 'Pre-flight check before execution'],
        ['mcpt doctor', 'Check CLI config and registry connectivity'],
      ],
    },
    {
      kind: 'data-table',
      id: 'trust',
      title: 'Trust Tiers',
      subtitle: 'Every tool gets a trust level and risk aura at a glance.',
      columns: ['Tier', 'Meaning'],
      rows: [
        ['Trusted', 'First-party or audited — safe for production'],
        ['Verified', 'Community-reviewed — meets quality bar'],
        ['Neutral', 'Published but unreviewed — use with caution'],
        ['Experimental', 'Early-stage — expect breaking changes'],
      ],
    },
    {
      kind: 'code-cards',
      id: 'workspace',
      title: 'Workspace Config',
      cards: [
        {
          title: 'mcp.yaml',
          code: 'schema_version: "0.1"\nname: "my-mcp-workspace"\n\nregistry:\n  source: "https://github.com/mcp-tool-shop-org/mcp-tool-registry"\n  ref: "v0.3.0"\n\ntools:\n  - file-compass\n  - id: tool-compass\n    ref: v1.0.0\n    grants:\n      - network',
        },
        {
          title: 'Pinning strategy',
          code: '# Pin the registry snapshot\nregistry:\n  ref: "v0.3.0"\n\n# Pin individual tools\ntools:\n  - id: my-tool\n    ref: v2.1.0\n\n# Both matter for reproducibility',
        },
      ],
    },
    {
      kind: 'data-table',
      id: 'docs',
      title: 'Documentation',
      columns: ['Document', 'Description'],
      rows: [
        ['HANDBOOK.md', 'Deep-dive: architecture, workspace model, trust, CI patterns'],
        ['CONTRIBUTING.md', 'How to contribute to mcpt'],
        ['CHANGELOG.md', 'Release history'],
        ['Registry Contract', 'Stability and metadata guarantees'],
      ],
    },
  ],
};
