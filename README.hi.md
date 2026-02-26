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

## एक नज़र में

- [mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry) के लिए **आधिकारिक क्लाइंट** - MCP टूल शॉप टूल का आधिकारिक स्रोत।
- `mcp.yaml` के माध्यम से **कार्यक्षेत्र प्रबंधन** - परियोजनाओं में टूल सेट घोषित करें, फिक्स करें और साझा करें।
- **विश्वसनीयता स्तर** (विश्वसनीय/सत्यापित/तटस्थ/प्रायोगिक) और **जोखिम संकेतक** जो क्षमता-स्तर के खतरों को एक नज़र में दिखाते हैं।
- **सुरक्षित-डिफ़ॉल्ट निष्पादन** - टूल डिफ़ॉल्ट रूप से स्टब मोड में चलते हैं, जब तक कि स्पष्ट रूप से सक्रिय न किए जाएं, और वास्तविक निष्पादन से पहले क्षमताएं प्रदान की जाती हैं।
- **रजिस्ट्री पिनिंग** - पुनरुत्पादन के लिए, रजिस्ट्री संदर्भ और व्यक्तिगत टूल संदर्भ दोनों को लॉक करें ताकि बिल्ड नियतात्मक हों।
- **समृद्ध टीयूआई** - सुलभ, CI-अनुकूल आउटपुट के लिए `--plain` और `NO_COLOR` समर्थन।

## स्थापना

### पायथन (अनुशंसित)

```bash
pip install mcp-select
```

> **`mcp-select` क्यों?** मॉडल कॉन्टेक्स्ट प्रोटोकॉल SDK के लिए आधिकारिक एंथ्रोपिक `mcp` पैकेज PyPI पर मौजूद है। हम `mcp-select` को पैकेज नाम के रूप में उपयोग करते हैं ताकि टकराव से बचा जा सके। CLI कमांड हमेशा `mcpt` होता है।

### npm रैपर

```bash
npx @mcptoolshop/mcpt          # one-shot
npm install -g @mcptoolshop/mcpt  # global install
```

npm पैकेज पोस्टइंस्टॉल हुक के माध्यम से पायथन `mcp-select` पैकेज को स्वचालित रूप से स्थापित करता है। पायथन 3.10+ की आवश्यकता है।

## शुरुआत कैसे करें

```bash
mcpt list --refresh        # Fetch the registry and browse available tools
mcpt init                  # Create mcp.yaml in the current directory
mcpt add file-compass      # Add a tool to your workspace
mcpt install file-compass  # Install the tool via pip
mcpt run file-compass      # Run in stub mode (safe by default)
```

## कमांड

| कमांड | विवरण |
| --------- | ------------- |
| `mcpt list` | रजिस्ट्री में उपलब्ध सभी टूल सूचीबद्ध करें। |
| `mcpt info <tool-id>` | किसी टूल के बारे में विस्तृत जानकारी दिखाएं। |
| `mcpt search <query>` | रैंक किए गए परिणामों के साथ टूल खोजें। |
| `mcpt init` | एक कार्यक्षेत्र (`mcp.yaml`) आरंभ करें। |
| `mcpt add <tool-id>` | कार्यक्षेत्र में एक टूल जोड़ें। |
| `mcpt remove <tool-id>` | कार्यक्षेत्र से एक टूल हटाएं। |
| `mcpt install <tool-id>` | एक टूल को वर्चुअल वातावरण में git के माध्यम से स्थापित करें। |
| `mcpt run <tool-id>` | एक टूल चलाएं (डिफ़ॉल्ट रूप से स्टब, वास्तविक निष्पादन के लिए `--mode restricted`)। |
| `mcpt grant <tool-id> <cap>` | एक टूल को एक क्षमता प्रदान करें। |
| `mcpt revoke <tool-id> <cap>` | एक टूल से एक क्षमता वापस लें। |
| `mcpt check <tool-id>` | निष्पादन से पहले प्रारंभिक जांच। |
| `mcpt doctor` | CLI कॉन्फ़िगरेशन और रजिस्ट्री कनेक्टिविटी की जांच करें। |
| `mcpt icons` | विज़ुअल-भाषा चीट शीट दिखाएं (विश्वसनीयता स्तर, जोखिम मार्कर, बैज)। |
| `mcpt bundles` | उपलब्ध टूल बंडलों की सूची दिखाएं। |
| `mcpt featured` | सुविधाजनक टूल और क्यूरेटेड संग्रह ब्राउज़ करें। |
| `mcpt facets` | रजिस्ट्री पहलुओं और आँकड़ों को दिखाएं। |
| `mcpt registry` | रजिस्ट्री स्थिति और उत्पत्ति के बारे में विस्तृत जानकारी दिखाएं। |

अधिकांश कमांड मशीन-पठनीय आउटपुट के लिए `--json` और रंग-मुक्त रेंडरिंग के लिए `--plain` स्वीकार करते हैं।

## कॉन्फ़िगरेशन

`mcpt` कार्यक्षेत्र कॉन्फ़िगरेशन के लिए `mcp.yaml` का उपयोग करता है:

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

### पिनिंग

जब आप `mcp.yaml` में `registry.ref: v0.3.0` सेट करते हैं, तो आप **रजिस्ट्री मेटाडेटा** को पिन करते हैं - आप टूल सूची का कौन सा संस्करण पढ़ रहे हैं। यह टूल-स्तर के संदर्भों से अलग है:

- **रजिस्ट्री संदर्भ** - टूल कैटलॉग का कौन सा स्नैपशॉट आप उपयोग कर रहे हैं।
- **टूल संदर्भ** - `mcpt add tool-id --ref v1.0.0` के साथ व्यक्तिगत टूल को पिन करें।

पुनरुत्पादन के लिए दोनों महत्वपूर्ण हैं। सुसंगत टूल खोज के लिए रजिस्ट्री को पिन करें; सुसंगत व्यवहार के लिए टूल को पिन करें।

## इकोसिस्टम

`mcpt` **[mcp-tool-registry](https://github.com/mcp-tool-shop-org/mcp-tool-registry)** के लिए आधिकारिक क्लाइंट है।

- **[पब्लिक एक्सप्लोरर](https://mcp-tool-shop-org.github.io/mcp-tool-registry/)** - वेब पर उपलब्ध टूल ब्राउज़ करें।
- **[रजिस्ट्री अनुबंध](https://github.com/mcp-tool-shop-org/mcp-tool-registry/blob/main/docs/contract.md)** - स्थिरता और मेटाडेटा गारंटी।
- **[एक टूल सबमिट करें](https://github.com/mcp-tool-shop-org/mcp-tool-registry/issues/new/choose)** - इकोसिस्टम में योगदान करें।

## दस्तावेज़

| दस्तावेज़ | विवरण |
| ---------- | ------------- |
| [HANDBOOK.md](HANDBOOK.md) | विस्तृत जानकारी: आर्किटेक्चर, कार्यक्षेत्र मॉडल, सुरक्षा और विश्वसनीयता, सीआई पैटर्न, अक्सर पूछे जाने वाले प्रश्न। |
| [CONTRIBUTING.md](CONTRIBUTING.md) | mcpt में कैसे योगदान करें। |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | समुदाय के नियम। |
| [CHANGELOG.md](CHANGELOG.md) | रिलीज़ का इतिहास। |

## विकास।

```bash
pip install -e ".[dev]"
pytest
```

## लाइसेंस।

[MIT](LICENSE)
