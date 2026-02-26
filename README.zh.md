<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  
            <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/mcpt/readme.png"
           alt="mcpt" width="400">
</p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/mcpt/actions/workflows/ci.yml"><img src="https://github.com/mcp-tool-shop-org/mcpt/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/mcp-select/"><img src="https://img.shields.io/pypi/v/mcp-select" alt="PyPI"></a>
  <a href="https://www.npmjs.com/package/@mcptoolshop/mcpt"><img src="https://img.shields.io/npm/v/@mcptoolshop/mcpt" alt="npm"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow" alt="MIT License"></a>
  <a href="https://mcp-tool-shop-org.github.io/mcpt/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page"></a>
</p>

---

## At a Glance

- **官方客户端**，用于 [mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry) -- MCP Tool Shop 工具的权威信息来源。
- 通过 `mcp.yaml` 进行 **工作区管理** -- 在项目之间声明、固定和共享工具集。
- **信任等级**（可信/已验证/中立/实验）和 **风险提示**，一目了然地显示工具的能力级别。
- **默认安全模式** -- 工具默认以模拟模式运行，只有在明确启用时才会执行，并且在执行前会强制执行能力授予。
- **注册表固定**，用于可重复性 -- 锁定注册表引用以及单个工具引用，以确保构建的确定性。
- 具有 **丰富文本用户界面 (TUI)**，支持 `--plain` 和 `NO_COLOR` 参数，提供易于访问且适合 CI 环境的输出。

## 安装

### Python (推荐)

```bash
pip install mcp-select
```

> **为什么选择 `mcp-select`？** 官方的 Anthropic `mcp` 包存在于 PyPI 上，用于 Model Context Protocol SDK。 我们使用 `mcp-select` 作为包名，以避免冲突。 CLI 命令始终是 `mcpt`。

### npm 包装器

```bash
npx @mcptoolshop/mcpt          # one-shot
npm install -g @mcptoolshop/mcpt  # global install
```

npm 包通过安装后钩子自动安装 Python `mcp-select` 包。 需要 Python 3.10 或更高版本。

## 入门

```bash
mcpt list --refresh        # Fetch the registry and browse available tools
mcpt init                  # Create mcp.yaml in the current directory
mcpt add file-compass      # Add a tool to your workspace
mcpt install file-compass  # Install the tool via pip
mcpt run file-compass      # Run in stub mode (safe by default)
```

## 命令

| 命令 | 描述 |
| --------- | ------------- |
| `mcpt list` | 列出注册表中所有可用的工具 |
| `mcpt info <tool-id>` | 显示有关工具的详细信息 |
| `mcpt search <query>` | 搜索工具，并按排名显示结果 |
| `mcpt init` | 初始化工作区 (`mcp.yaml`) |
| `mcpt add <tool-id>` | 将工具添加到工作区 |
| `mcpt remove <tool-id>` | 从工作区中删除工具 |
| `mcpt install <tool-id>` | 通过 git 将工具安装到虚拟环境中 |
| `mcpt run <tool-id>` | 运行工具（默认以模拟模式运行，使用 `--mode restricted` 参数进行实际执行） |
| `mcpt grant <tool-id> <cap>` | 授予工具某种能力 |
| `mcpt revoke <tool-id> <cap>` | 撤销工具的某种能力 |
| `mcpt check <tool-id>` | 执行前进行预检查 |
| `mcpt doctor` | 检查 CLI 配置和注册表连接 |
| `mcpt icons` | 显示视觉语言参考表（信任等级、风险标记、徽章） |
| `mcpt bundles` | 列出可用的工具包 |
| `mcpt featured` | 浏览精选工具和 curated 集合 |
| `mcpt facets` | 显示注册表的统计信息和状态 |
| `mcpt registry` | 显示注册表的详细状态和来源信息 |

大多数命令都支持 `--json` 参数，用于生成机器可读的输出，以及 `--plain` 参数，用于生成不带颜色的输出。

## 配置

`mcpt` 使用 `mcp.yaml` 文件进行工作区配置：

```yaml
schema_version: "0.1"
name: "my-mcp-workspace"

registry:
  source: "https://github.com/mcp-tool-shop-org/mcp-tool-registry"
  ref: "v0.3.0"

tools:
  - file-compass
  - id: tool-compass
    ref: v1.0.0
    grants:
      - network

run:
  safe_by_default: true

ui:
  sigil: unicode   # unicode | ascii | off
  badges: on       # on | off
```

### 固定

当你在 `mcp.yaml` 中设置 `registry.ref: v0.3.0` 时，你是在固定 **注册表元数据**，即你读取的工具列表的版本。 这与工具级别的引用是分开的：

- **注册表引用** -- 你使用的工具目录的快照。
- **工具引用** -- 使用 `mcpt add tool-id --ref v1.0.0` 固定单个工具。

两者都对可重复性很重要。 固定注册表以确保一致的工具发现；固定工具以确保一致的行为。

## 生态系统

`mcpt` 是 **[mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry)** 的官方客户端。

- **[公共浏览器](https://mcp-tool-shop-org.github.io/mcp-tool-registry/)** -- 在 Web 上浏览可用的工具。
- **[注册表协议](https://github.com/mcp-tool-shop-org/mcp-tool-registry/blob/main/docs/contract.md)** -- 稳定性和元数据保证。
- **[提交工具](https://github.com/mcp-tool-shop-org/mcp-tool-registry/issues/new/choose)** -- 贡献到生态系统。

## 文档

| 文档 | 描述 |
| ---------- | ------------- |
| [HANDBOOK.md](HANDBOOK.md) | 深入指南：架构、工作空间模型、安全与信任、CI 模式、常见问题解答 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 如何为 mcpt 项目贡献代码 |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | 社区规范 |
| [CHANGELOG.md](CHANGELOG.md) | 发布历史 |

## 开发

```bash
pip install -e ".[dev]"
pytest
```

## 许可证

[MIT](LICENSE)
