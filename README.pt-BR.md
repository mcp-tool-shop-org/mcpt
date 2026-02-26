<p align="center">
  <a href="README.ja.md">日本語</a> | <a href="README.zh.md">中文</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.hi.md">हिन्दी</a> | <a href="README.it.md">Italiano</a> | <a href="README.pt-BR.md">Português (BR)</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/mcp-tool-shop-org/mcpt/main/assets/logo-mcpt.png" alt="mcpt" width="400">
</p>

<p align="center">
  <a href="https://github.com/mcp-tool-shop-org/mcpt/actions/workflows/ci.yml"><img src="https://github.com/mcp-tool-shop-org/mcpt/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/mcp-select/"><img src="https://img.shields.io/pypi/v/mcp-select" alt="PyPI"></a>
  <a href="https://www.npmjs.com/package/@mcptoolshop/mcpt"><img src="https://img.shields.io/npm/v/@mcptoolshop/mcpt" alt="npm"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow" alt="MIT License"></a>
  <a href="https://mcp-tool-shop-org.github.io/mcpt/"><img src="https://img.shields.io/badge/Landing_Page-live-blue" alt="Landing Page"></a>
</p>

---

## Em resumo

- **Cliente oficial** para o [mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry) – a fonte canônica de informações sobre as ferramentas do MCP Tool Shop.
- **Gerenciamento de ambientes de trabalho** via `mcp.yaml` – declare, fixe e compartilhe conjuntos de ferramentas entre projetos.
- **Níveis de confiança** (confiável / verificado / neutro / experimental) e **níveis de risco** que exibem o nível de perigo das ferramentas de forma clara.
- **Execução segura por padrão** – as ferramentas são executadas no modo de simulação, a menos que sejam explicitamente ativadas, e as permissões são aplicadas antes da execução real.
- **Fixação do registro** para reprodutibilidade – bloqueie a referência do registro *e* as referências individuais das ferramentas para que as compilações sejam determinísticas.
- **Interface de usuário (TUI) avançada** com suporte para `--plain` e `NO_COLOR` para uma saída acessível e compatível com sistemas de integração contínua (CI).

## Instalação

### Python (recomendado)

```bash
pip install mcp-select
```

> **Por que `mcp-select`?** O pacote oficial `mcp` da Anthropic está disponível no PyPI para o
> SDK do Protocolo de Contexto do Modelo. Usamos `mcp-select` como nome do pacote para evitar
> conflitos. O comando da interface de linha de comando (CLI) é sempre `mcpt`.

### Wrapper npm

```bash
npx @mcptoolshop/mcpt          # one-shot
npm install -g @mcptoolshop/mcpt  # global install
```

O pacote npm instala automaticamente o pacote Python `mcp-select` por meio de um hook de pós-instalação. É necessário o Python 3.10 ou superior.

## Primeiros Passos

```bash
mcpt list --refresh        # Fetch the registry and browse available tools
mcpt init                  # Create mcp.yaml in the current directory
mcpt add file-compass      # Add a tool to your workspace
mcpt install file-compass  # Install the tool via pip
mcpt run file-compass      # Run in stub mode (safe by default)
```

## Comandos

| Comando | Descrição |
| --------- | ------------- |
| `mcpt list` | Lista todas as ferramentas disponíveis no registro. |
| `mcpt info <tool-id>` | Mostra informações detalhadas sobre uma ferramenta. |
| `mcpt search <query>` | Pesquisa ferramentas com resultados classificados. |
| `mcpt init` | Inicializa um ambiente de trabalho (`mcp.yaml`). |
| `mcpt add <tool-id>` | Adiciona uma ferramenta ao ambiente de trabalho. |
| `mcpt remove <tool-id>` | Remove uma ferramenta do ambiente de trabalho. |
| `mcpt install <tool-id>` | Instala uma ferramenta via Git em um ambiente virtual. |
| `mcpt run <tool-id>` | Executa uma ferramenta (modo de simulação por padrão, `--mode restricted` para execução real). |
| `mcpt grant <tool-id> <cap>` | Concede uma permissão a uma ferramenta. |
| `mcpt revoke <tool-id> <cap>` | Revoga uma permissão de uma ferramenta. |
| `mcpt check <tool-id>` | Verifica as configurações antes da execução. |
| `mcpt doctor` | Verifica a configuração da interface de linha de comando e a conectividade com o registro. |
| `mcpt icons` | Mostra o guia visual (níveis de confiança, marcadores de risco, selos). |
| `mcpt bundles` | Lista os conjuntos de ferramentas disponíveis. |
| `mcpt featured` | Navega pelas ferramentas em destaque e coleções selecionadas. |
| `mcpt facets` | Mostra as estatísticas e os aspectos do registro. |
| `mcpt registry` | Mostra o status detalhado do registro e a origem. |

A maioria dos comandos aceita `--json` para saída legível por máquina e `--plain` para renderização sem cores.

## Configuração

O `mcpt` usa `mcp.yaml` para a configuração do ambiente de trabalho:

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

### Fixação

Quando você define `registry.ref: v0.3.0` em `mcp.yaml`, você fixa os **metadados do registro** – qual versão da lista de ferramentas você está usando. Isso é diferente das referências de nível de ferramenta:

- **Referência do registro** – qual instantâneo do catálogo de ferramentas você está usando.
- **Referência da ferramenta** – fixe ferramentas individuais com `mcpt add tool-id --ref v1.0.0`.

Ambos são importantes para a reprodutibilidade. Fixe o registro para uma descoberta consistente de ferramentas; fixe as ferramentas para um comportamento consistente.

## Ecossistema

O `mcpt` é o cliente oficial para o **[mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry)**.

- **[Explorador Público](https://mcp-tool-shop-org.github.io/mcp-tool-registry/)** – Navegue pelas ferramentas disponíveis na web.
- **[Contrato do Registro](https://github.com/mcp-tool-shop-org/mcp-tool-registry/blob/main/docs/contract.md)** – Estabilidade e garantias de metadados.
- **[Enviar uma Ferramenta](https://github.com/mcp-tool-shop-org/mcp-tool-registry/issues/new/choose)** – Contribua para o ecossistema.

## Documentação

| Documento | Descrição |
| ---------- | ------------- |
| [HANDBOOK.md](HANDBOOK.md) | Guia detalhado: arquitetura, modelo de trabalho, segurança e confiança, padrões de integração contínua, perguntas frequentes. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Como contribuir para o projeto mcpt. |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Normas da comunidade. |
| [CHANGELOG.md](CHANGELOG.md) | Histórico de lançamentos. |

## Desenvolvimento

```bash
pip install -e ".[dev]"
pytest
```

## Licença

[MIT](LICENSE)
