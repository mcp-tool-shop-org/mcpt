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

- **Cliente oficial** para el [mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry): la fuente de información canónica para las herramientas de MCP Tool Shop.
- **Gestión de espacios de trabajo** a través de `mcp.yaml`: declare, fije y comparta conjuntos de herramientas entre proyectos.
- **Niveles de confianza** (confiables / verificados / neutrales / experimentales) y **indicadores de riesgo** que muestran el nivel de peligro de las capacidades de un vistazo.
- **Ejecución segura por defecto**: las herramientas se ejecutan en modo de simulación a menos que se especifique explícitamente, y se aplican los permisos de capacidades antes de la ejecución real.
- **Fijación del registro** para la reproducibilidad: bloquea la referencia del registro y las referencias individuales de las herramientas para que las compilaciones sean deterministas.
- **Interfaz de usuario basada en texto (TUI) avanzada** con soporte para `--plain` y `NO_COLOR` para una salida accesible y compatible con CI.

## Instalación

### Python (recomendado)

```bash
pip install mcp-select
```

> **¿Por qué `mcp-select`?** El paquete oficial `mcp` de Anthropic existe en PyPI para el
> SDK de Protocolo de Contexto de Modelo. Utilizamos `mcp-select` como nombre del paquete para evitar
> conflictos. El comando de la interfaz de línea de comandos (CLI) es siempre `mcpt`.

### Envoltorio npm

```bash
npx @mcptoolshop/mcpt          # one-shot
npm install -g @mcptoolshop/mcpt  # global install
```

El paquete npm instala automáticamente el paquete de Python `mcp-select` a través de un gancho de postinstalación. Se requiere Python 3.10 o superior.

## Cómo empezar

```bash
mcpt list --refresh        # Fetch the registry and browse available tools
mcpt init                  # Create mcp.yaml in the current directory
mcpt add file-compass      # Add a tool to your workspace
mcpt install file-compass  # Install the tool via pip
mcpt run file-compass      # Run in stub mode (safe by default)
```

## Comandos

| Comando | Descripción |
| --------- | ------------- |
| `mcpt list` | Lista todas las herramientas disponibles en el registro. |
| `mcpt info <tool-id>` | Muestra información detallada sobre una herramienta. |
| `mcpt search <query>` | Busca herramientas con resultados clasificados. |
| `mcpt init` | Inicializa un espacio de trabajo (`mcp.yaml`). |
| `mcpt add <tool-id>` | Añade una herramienta al espacio de trabajo. |
| `mcpt remove <tool-id>` | Elimina una herramienta del espacio de trabajo. |
| `mcpt install <tool-id>` | Instala una herramienta a través de git en un entorno virtual. |
| `mcpt run <tool-id>` | Ejecuta una herramienta (modo de simulación por defecto, `--mode restricted` para la ejecución real). |
| `mcpt grant <tool-id> <cap>` | Otorga una capacidad a una herramienta. |
| `mcpt revoke <tool-id> <cap>` | Revoca una capacidad de una herramienta. |
| `mcpt check <tool-id>` | Comprobación previa a la ejecución. |
| `mcpt doctor` | Comprueba la configuración de la CLI y la conectividad del registro. |
| `mcpt icons` | Muestra la hoja de trucos de lenguaje visual (niveles de confianza, indicadores de riesgo, insignias). |
| `mcpt bundles` | Lista los conjuntos de herramientas disponibles. |
| `mcpt featured` | Explora herramientas destacadas y colecciones curadas. |
| `mcpt facets` | Muestra las facetas y estadísticas del registro. |
| `mcpt registry` | Muestra el estado y el origen detallados del registro. |

La mayoría de los comandos aceptan `--json` para una salida legible por máquina y `--plain` para una representación sin color.

## Configuración

`mcpt` utiliza `mcp.yaml` para la configuración del espacio de trabajo:

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

### Fijación

Cuando estableces `registry.ref: v0.3.0` en `mcp.yaml`, fijas los **metadatos del registro**: qué versión de la lista de herramientas estás utilizando. Esto es independiente de las referencias a nivel de herramienta:

- **Referencia del registro**: qué instantánea del catálogo de herramientas estás utilizando.
- **Referencia de la herramienta**: fija herramientas individuales con `mcpt add tool-id --ref v1.0.0`.

Ambos son importantes para la reproducibilidad. Fija el registro para una detección consistente de herramientas; fija las herramientas para un comportamiento consistente.

## Ecosistema

`mcpt` es el cliente oficial para el **[mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry)**.

- **[Explorador público](https://mcp-tool-shop-org.github.io/mcp-tool-registry/)** -- Explora las herramientas disponibles en la web.
- **[Contrato del registro](https://github.com/mcp-tool-shop-org/mcp-tool-registry/blob/main/docs/contract.md)** -- Garantías de estabilidad y metadatos.
- **[Enviar una herramienta](https://github.com/mcp-tool-shop-org/mcp-tool-registry/issues/new/choose)** -- Contribuye al ecosistema.

## Documentación

| Documento | Descripción |
| ---------- | ------------- |
| [HANDBOOK.md](HANDBOOK.md) | Guía detallada: arquitectura, modelo de trabajo, seguridad y confianza, patrones de integración continua, preguntas frecuentes. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Cómo contribuir a mcpt. |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Normas de la comunidad. |
| [CHANGELOG.md](CHANGELOG.md) | Historial de versiones. |

## Desarrollo

```bash
pip install -e ".[dev]"
pytest
```

## Licencia

[MIT](LICENSE)
