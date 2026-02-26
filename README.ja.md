<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/brand/main/logos/mcpt/readme.png" alt="mcpt" width="400">
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

- **公式クライアント**：[mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry) - MCP Tool Shopツールの信頼できる情報源
- **ワークスペース管理**：`mcp.yaml` を使用して、ツールセットを宣言、固定し、プロジェクト間で共有
- **信頼レベル**（信頼済み/検証済み/中立/実験的）と、**リスクレベル**を表示し、ツールの機能レベルのリスクを視覚的に把握
- **安全第一の実行**：ツールはデフォルトでスタブモードで実行され、実際の実行を行う前に、明示的に許可された場合にのみ実行されます。
- **レジストリの固定**：再現性を確保するために、レジストリの参照情報だけでなく、個々のツールの参照情報も固定します。
- **リッチなTUI**：アクセシビリティとCI環境での利用を考慮し、`--plain` および `NO_COLOR` オプションに対応

## インストール

### Python (推奨)

```bash
pip install mcp-select
```

> **なぜ `mcp-select` なのか？**
> Model Context Protocol SDK の公式 Anthropic パッケージは PyPI に存在します。
> `mcp-select` は、パッケージ名として競合を避けるために使用しています。
> コマンドラインインターフェース (CLI) のコマンドは常に `mcpt` です。

### npm パッケージ

```bash
npx @mcptoolshop/mcpt          # one-shot
npm install -g @mcptoolshop/mcpt  # global install
```

npm パッケージは、インストール時に Python の `mcp-select` パッケージを自動的にインストールします。Python 3.10 以降が必要です。

## Getting Started

```bash
mcpt list --refresh        # Fetch the registry and browse available tools
mcpt init                  # Create mcp.yaml in the current directory
mcpt add file-compass      # Add a tool to your workspace
mcpt install file-compass  # Install the tool via pip
mcpt run file-compass      # Run in stub mode (safe by default)
```

## Commands

| Command | Description |
| --------- | ------------- |
| `mcpt list` | レジストリに登録されているすべてのツールを表示 |
| `mcpt info <tool-id>` | ツールの詳細情報を表示 |
| `mcpt search <query>` | ツールを検索し、ランキングされた結果を表示 |
| `mcpt init` | ワークスペース (`mcp.yaml`) を初期化 |
| `mcpt add <tool-id>` | ワークスペースにツールを追加 |
| `mcpt remove <tool-id>` | ワークスペースからツールを削除 |
| `mcpt install <tool-id>` | git リポジトリから仮想環境にツールをインストール |
| `mcpt run <tool-id>` | ツールを実行（デフォルトはスタブモード、実際の実行には `--mode restricted` を指定） |
| `mcpt grant <tool-id> <cap>` | ツールに機能（capability）を付与 |
| `mcpt revoke <tool-id> <cap>` | ツールから機能を取り消し |
| `mcpt check <tool-id>` | 実行前の事前チェック |
| `mcpt doctor` | CLI の設定とレジストリへの接続を確認 |
| `mcpt icons` | 視覚的な情報（信頼レベル、リスクマーカー、バッジ）を表示 |
| `mcpt bundles` | 利用可能なツールバンドルを表示 |
| `mcpt featured` | おすすめのツールとキュレーションされたコレクションを閲覧 |
| `mcpt facets` | レジストリの統計情報とメタデータを表示 |
| `mcpt registry` | レジストリの詳細な状態と情報源を表示 |

ほとんどのコマンドは、機械可読な出力のために `--json` オプション、およびカラー表示を無効にするために `--plain` オプションをサポートしています。

## Configuration

mcpt は、ワークスペースの設定に `mcp.yaml` を使用します。

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

### Pinning

`mcp.yaml` で `registry.ref: v0.3.0` を設定すると、**レジストリのメタデータ**（どのバージョンのツールリストを使用しているか）を固定します。これは、個々のツールの参照情報とは異なります。

- **レジストリ参照**：使用するツールカタログのバージョン
- **ツール参照**：`mcpt add tool-id --ref v1.0.0` で個々のツールを固定

どちらも再現性に重要です。レジストリを固定することで、一貫したツール検出を保証し、ツールを固定することで、一貫した動作を保証します。

## Ecosystem

mcpt は、**[mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry)** の公式クライアントです。

- **[Public Explorer](https://mcp-tool-shop-org.github.io/mcp-tool-registry/)**：Web ブラウザで利用可能なツールを閲覧
- **[Registry Contract](https://github.com/mcp-tool-shop-org/mcp-tool-registry/blob/main/docs/contract.md)**：安定性とメタデータに関する保証
- **[Submit a Tool](https://github.com/mcp-tool-shop-org/mcp-tool-registry/issues/new/choose)**：エコシステムへの貢献

## Docs

| Document | Description |
| ---------- | ------------- |
| [HANDBOOK.md](HANDBOOK.md) | 詳細ガイド：アーキテクチャ、ワークスペースモデル、信頼と安全、CIのパターン、よくある質問 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | mcptへの貢献方法 |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | コミュニティの規約 |
| [CHANGELOG.md](CHANGELOG.md) | リリース履歴 |

## 開発

```bash
pip install -e ".[dev]"
pytest
```

## ライセンス

[MIT](LICENSE)
