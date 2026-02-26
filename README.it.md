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

- **Client ufficiale** per il [mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry) – la fonte ufficiale e definitiva per gli strumenti di MCP Tool Shop.
- **Gestione degli ambienti di lavoro** tramite `mcp.yaml` – dichiarazione, blocco e condivisione di set di strumenti tra i progetti.
- **Livelli di affidabilità** (affidabile / verificato / neutro / sperimentale) e **indicatori di rischio** che mostrano a colpo d'occhio il livello di pericolosità delle funzionalità.
- **Esecuzione sicura per impostazione predefinita** – gli strumenti vengono eseguiti in modalità "stub" a meno che non vengano esplicitamente attivati, con le autorizzazioni applicate prima dell'esecuzione effettiva.
- **Blocco del registro** per la riproducibilità – blocca sia il riferimento del registro *che* i singoli riferimenti degli strumenti, in modo che le build siano deterministiche.
- **Interfaccia utente testuale (TUI) avanzata** con supporto per `--plain` e `NO_COLOR` per un output accessibile e compatibile con i sistemi di integrazione continua (CI).

## Installazione

### Python (consigliato)

```bash
pip install mcp-select
```

> **Perché `mcp-select`?** Esiste il pacchetto ufficiale `mcp` di Anthropic su PyPI per il
> Model Context Protocol SDK. Utilizziamo `mcp-select` come nome del pacchetto per evitare
> conflitti. Il comando della riga di comando è sempre `mcpt`.

### Wrapper npm

```bash
npx @mcptoolshop/mcpt          # one-shot
npm install -g @mcptoolshop/mcpt  # global install
```

Il pacchetto npm installa automaticamente il pacchetto Python `mcp-select` tramite un hook di post-installazione. È richiesta la versione 3.10 o superiore di Python.

## Come Iniziare

```bash
mcpt list --refresh        # Fetch the registry and browse available tools
mcpt init                  # Create mcp.yaml in the current directory
mcpt add file-compass      # Add a tool to your workspace
mcpt install file-compass  # Install the tool via pip
mcpt run file-compass      # Run in stub mode (safe by default)
```

## Comandi

| Comando | Descrizione |
| --------- | ------------- |
| `mcpt list` | Elenca tutti gli strumenti disponibili nel registro. |
| `mcpt info <tool-id>` | Mostra informazioni dettagliate su uno strumento. |
| `mcpt search <query>` | Cerca strumenti con risultati ordinati. |
| `mcpt init` | Inizializza un ambiente di lavoro (`mcp.yaml`). |
| `mcpt add <tool-id>` | Aggiungi uno strumento all'ambiente di lavoro. |
| `mcpt remove <tool-id>` | Rimuovi uno strumento dall'ambiente di lavoro. |
| `mcpt install <tool-id>` | Installa uno strumento tramite git in un ambiente virtuale. |
| `mcpt run <tool-id>` | Esegui uno strumento (in modalità "stub" per impostazione predefinita, `--mode restricted` per l'esecuzione effettiva). |
| `mcpt grant <tool-id> <cap>` | Concedi un'autorizzazione a uno strumento. |
| `mcpt revoke <tool-id> <cap>` | Revoca un'autorizzazione da uno strumento. |
| `mcpt check <tool-id>` | Controllo preliminare prima dell'esecuzione. |
| `mcpt doctor` | Verifica la configurazione della riga di comando e la connettività del registro. |
| `mcpt icons` | Mostra la guida visiva (livelli di affidabilità, indicatori di rischio, badge). |
| `mcpt bundles` | Elenca i set di strumenti disponibili. |
| `mcpt featured` | Esplora gli strumenti in evidenza e le raccolte curate. |
| `mcpt facets` | Mostra le statistiche e le caratteristiche del registro. |
| `mcpt registry` | Mostra lo stato dettagliato del registro e le informazioni sulla sua origine. |

La maggior parte dei comandi accetta `--json` per un output leggibile dalle macchine e `--plain` per una visualizzazione senza colori.

## Configurazione

`mcpt` utilizza `mcp.yaml` per la configurazione dell'ambiente di lavoro:

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

### Blocco (Pinning)

Quando imposti `registry.ref: v0.3.0` in `mcp.yaml`, blocchi i **metadati del registro** – la versione dell'elenco degli strumenti che stai utilizzando. Questo è separato dai riferimenti a livello di strumento:

- **Riferimento del registro** – lo snapshot del catalogo degli strumenti che stai utilizzando.
- **Riferimento dello strumento** – blocca singoli strumenti con `mcpt add tool-id --ref v1.0.0`.

Entrambi sono importanti per la riproducibilità. Blocca il registro per una scoperta coerente degli strumenti; blocca gli strumenti per un comportamento coerente.

## Ecosistema

`mcpt` è il client ufficiale per il **[mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry)**.

- **[Esplora Pubblica](https://mcp-tool-shop-org.github.io/mcp-tool-registry/)** – Esplora gli strumenti disponibili sul web.
- **[Contratto del Registro](https://github.com/mcp-tool-shop-org/mcp-tool-registry/blob/main/docs/contract.md)** – Garanzie di stabilità e metadati.
- **[Invia uno Strumento](https://github.com/mcp-tool-shop-org/mcp-tool-registry/issues/new/choose)** – Contribuisci all'ecosistema.

## Documentazione

| Documento | Descrizione |
| ---------- | ------------- |
| [HANDBOOK.md](HANDBOOK.md) | Guida approfondita: architettura, modello di lavoro, sicurezza e affidabilità, modelli di integrazione continua, domande frequenti. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Come contribuire a mcpt. |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Linee guida della comunità. |
| [CHANGELOG.md](CHANGELOG.md) | Cronologia delle versioni. |

## Sviluppo

```bash
pip install -e ".[dev]"
pytest
```

## Licenza

[MIT](LICENSE)
