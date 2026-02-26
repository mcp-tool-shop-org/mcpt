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

- **Client officiel** pour le [mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry) -- la source de référence pour les outils MCP Tool Shop.
- **Gestion des espaces de travail** via `mcp.yaml` -- déclaration, fixation et partage des ensembles d'outils entre les projets.
- **Niveaux de confiance** (fiable / vérifié / neutre / expérimental) et **indicateurs de risque** qui permettent de visualiser rapidement le niveau de dangerosité des outils.
- **Exécution sécurisée par défaut** : les outils fonctionnent en mode "stub" (simulé) sauf indication contraire, et les autorisations sont appliquées avant l'exécution réelle.
- **Fixation du registre** pour la reproductibilité : verrouillage de la référence du registre *et* des références individuelles des outils afin de garantir des constructions déterministes.
- **Interface utilisateur riche** avec prise en charge de `--plain` et `NO_COLOR` pour une sortie accessible et compatible avec les systèmes d'intégration continue.

## Installation

### Python (recommandé)

```bash
pip install mcp-select
```

> **Pourquoi `mcp-select` ?** Le paquet officiel `mcp` d'Anthropic est disponible sur PyPI pour le
> SDK du protocole de contexte de modèle. Nous utilisons `mcp-select` comme nom de paquet pour éviter
> les conflits. La commande de l'interface en ligne de commande est toujours `mcpt`.

### Wrapper npm

```bash
npx @mcptoolshop/mcpt          # one-shot
npm install -g @mcptoolshop/mcpt  # global install
```

Le paquet npm installe automatiquement le paquet Python `mcp-select` via un crochet post-installation. Python 3.10+ est requis.

## Premiers pas

```bash
mcpt list --refresh        # Fetch the registry and browse available tools
mcpt init                  # Create mcp.yaml in the current directory
mcpt add file-compass      # Add a tool to your workspace
mcpt install file-compass  # Install the tool via pip
mcpt run file-compass      # Run in stub mode (safe by default)
```

## Commandes

| Commande | Description |
| --------- | ------------- |
| `mcpt list` | Liste tous les outils disponibles dans le registre. |
| `mcpt info <tool-id>` | Affiche des informations détaillées sur un outil. |
| `mcpt search <query>` | Recherche des outils avec des résultats classés. |
| `mcpt init` | Initialise un espace de travail (`mcp.yaml`). |
| `mcpt add <tool-id>` | Ajoute un outil à l'espace de travail. |
| `mcpt remove <tool-id>` | Supprime un outil de l'espace de travail. |
| `mcpt install <tool-id>` | Installe un outil via git dans un environnement virtuel. |
| `mcpt run <tool-id>` | Exécute un outil (mode "stub" par défaut, `--mode restricted` pour une exécution réelle). |
| `mcpt grant <tool-id> <cap>` | Accorde une autorisation à un outil. |
| `mcpt revoke <tool-id> <cap>` | Révoque une autorisation d'un outil. |
| `mcpt check <tool-id>` | Vérification préalable avant l'exécution. |
| `mcpt doctor` | Vérifie la configuration de l'interface en ligne de commande et la connectivité au registre. |
| `mcpt icons` | Affiche le guide visuel des outils (niveaux de confiance, indicateurs de risque, badges). |
| `mcpt bundles` | Liste les ensembles d'outils disponibles. |
| `mcpt featured` | Parcourez les outils mis en avant et les collections thématiques. |
| `mcpt facets` | Affiche les facettes et les statistiques du registre. |
| `mcpt registry` | Affiche l'état détaillé du registre et son origine. |

La plupart des commandes acceptent `--json` pour une sortie lisible par machine et `--plain` pour une sortie sans couleurs.

## Configuration

`mcpt` utilise `mcp.yaml` pour la configuration de l'espace de travail :

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

### Fixation

Lorsque vous définissez `registry.ref: v0.3.0` dans `mcp.yaml`, vous fixez les **métadonnées du registre** : la version de la liste des outils que vous utilisez. Cela est distinct des références au niveau de l'outil :

- **Référence du registre** : la version du catalogue d'outils que vous utilisez.
- **Référence de l'outil** : fixez les outils individuels avec `mcpt add tool-id --ref v1.0.0`.

Les deux sont importants pour la reproductibilité. Fixez le registre pour une découverte cohérente des outils ; fixez les outils pour un comportement cohérent.

## Écosystème

`mcpt` est le client officiel pour le **[mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry)**.

- **[Explorateur public](https://mcp-tool-shop-org.github.io/mcp-tool-registry/)** : Parcourez les outils disponibles sur le web.
- **[Contrat du registre](https://github.com/mcp-tool-shop-org/mcp-tool-registry/blob/main/docs/contract.md)** : Garanties de stabilité et de métadonnées.
- **[Soumettre un outil](https://github.com/mcp-tool-shop-org/mcp-tool-registry/issues/new/choose)** : Contribuez à l'écosystème.

## Documentation

| Documentation | Description |
| ---------- | ------------- |
| [HANDBOOK.md](HANDBOOK.md) | Guide détaillé : architecture, modèle de travail, sécurité et confiance, modèles de CI, FAQ. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Comment contribuer à mcpt. |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Normes de la communauté. |
| [CHANGELOG.md](CHANGELOG.md) | Historique des versions. |

## Développement

```bash
pip install -e ".[dev]"
pytest
```

## Licence

[MIT](LICENSE)
