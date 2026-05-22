# MarketSpy AI

Local AI-powered Tokopedia marketplace scraper with automatic model orchestration.

**Project Status:** AI Orchestrator with rule engine fallback, automatic model selection, zero manual configuration.

## Features

- **Dual Scraping Engines:** Puppeteer (primary) + Selenium Rollback (failover)
- **AI Orchestrator:** Automatic cascade routing to installed Ollama models
- **Intent-Aware Filtering:** Query-aware product category matching
- **Rule Engine:** Deterministic fast filtering before LLM calls
- **Fallback System:** Works with rules only if no Ollama models installed
- **Budget Filtering:** Range-aware price filtering (optional)
- **Feedback Learning:** User corrections improve classifier over time
- **Production-Ready UI:** Dark theme, real-time progress, mobile-friendly

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Ollama (https://ollama.ai)

### Install Ollama Models (Required)

```bash
ollama pull gemma3:4b          # Main classifier
ollama pull llama3.2:3b        # Fast fallback
# Optional:
ollama pull phi4-mini          # JSON repair
ollama pull nomic-embed-text   # Semantic search
```

### Install Project

```bash
# Clone & setup
git clone <repo_url>
cd RB-C1
python -m pip install -r requirements.txt
npm install

# Run
python app.py

# Open browser
http://127.0.0.1:3000
```

## Supported Ollama Models

**ONLY these models work:**
- ✅ gemma3:4b (4GB VRAM) - recommended
- ✅ llama3.2:3b (3GB VRAM) - fast fallback
- ✅ phi4-mini (2GB VRAM) - JSON repair
- ✅ nomic-embed-text (0.3GB VRAM) - semantic search

**NOT supported:**
- ❌ qwen2.5:14b (removed - too slow)
- ❌ Any model outside the allowed list

## Architecture

### AI Decision Flow

```
Product arrives
    ↓
Rule Engine (fast)
├─ Obvious accept? → done
├─ Obvious reject? → done
└─ Borderline? → LLM
    ↓
Intent Detection
├─ "laptop gaming" → gaming laptops accepted
├─ "casing iphone" → accessories accepted
└─ "iphone" → accessories rejected
    ↓
Semantic Search (optional)
├─ If nomic-embed-text installed
└─ Helps match similar products
    ↓
LLM Classifier (cascade)
├─ Try gemma3:4b (if installed)
├─ Fallback: llama3.2:3b (if installed)
└─ Skip if both missing
    ↓
JSON Repair (if needed)
├─ Try phi4-mini (if installed)
└─ Fallback: rule confidence
    ↓
Result: accepted/rejected with confidence
```

**Key Insight:** Rule engine handles 70-80% of products. LLM only sees 20-30% (borderline cases).

## Configuration

Edit `src/config.py` for:
- Model timeouts: `OLLAMA_TIMEOUT_SECONDS = 12`
- Filtering thresholds: `RULE_ACCEPT_THRESHOLD = 0.72`
- Result count: `TARGET_COUNT_DEFAULT = 50`
- Performance: `AI_BATCH_SIZE = 8`

All settings have sensible defaults for Ryzen 7 7730U with 16GB RAM.

## API Endpoints

### Search

```
POST /api/search
{
  "query": "laptop gaming",
  "target_count": 50,
  "budget": null,
  "tolerance": 20,
  "use_ai": true,
  "engine_mode": "auto"
}
```

### Progress

```
GET /api/progress/{search_id}
```

### Results

```
GET /api/result/{search_id}
```

### AI Status

```
GET /api/ai/status
```

Returns installed models and capabilities.

### Feedback

```
POST /api/feedback
{
  "search_id": "...",
  "product_id": "...",
  "user_action": "salah",
  "selected_reasons": ["Produk tidak relevan"],
  "query": "laptop gaming"
}
```

## Troubleshooting

### No AI models detected

```bash
# Ensure Ollama is running
ollama serve

# In another terminal, pull a model
ollama pull gemma3:4b

# Refresh browser - auto-detects
```

### Search hangs on AI filtering

```bash
# Restart Ollama
ollama serve

# Check model is responsive
curl http://127.0.0.1:11434/api/tags
```

### Only 10 products returned (wanted 50)

1. Lower `RULE_REVIEW_THRESHOLD` in config (currently 0.45)
2. Disable budget or increase tolerance
3. Try broader query (e.g., "gaming laptop" vs "gaming laptop cooler")

### Results have low confidence

Lower thresholds in `config.py`:
```python
RULE_ACCEPT_THRESHOLD = 0.68  # Was 0.72
RULE_REVIEW_THRESHOLD = 0.40  # Was 0.45
```

## Performance Tips

**For Ryzen 7 7730U:**
- Use only gemma3:4b (4GB VRAM max)
- Skip semantic search (disable nomic-embed-text)
- Set AI_BATCH_SIZE = 4 (vs 8)
- OLLAMA_TIMEOUT_SECONDS = 20 (vs 12)

**For faster results:**
- Request target_count = 25 (vs 50)
- Use engine_mode = "puppeteer" (faster, less reliable)
- Disable budget filtering

**For more accuracy:**
- Install all 4 models
- Request target_count = 100, keep top 50
- Provide 20-30 feedback corrections

## Changes from Previous Version

**What was removed:**
- ❌ qwen2.5:14b model (too slow on laptop)
- ❌ Manual AI mode dropdown
- ❌ Hardcoded model selection

**What was added:**
- ✅ AI Orchestrator (auto routing)
- ✅ Model auto-detection
- ✅ Intent-aware classification
- ✅ Semantic search (optional)
- ✅ Better fallback handling

**Performance improvement:**
- 3-5x faster (rule-first, LLM-only for borderline)
- 70% fewer LLM calls
- Works without any Ollama models

## Development

### Run Tests

```bash
python -m pytest tests/ -v
```

### Debug Logs

Enable verbose logging:
```bash
DEBUG=1 python app.py
```

Debug files saved to: `data/debug/{search_id}/`

### Files Structure

```
src/
├── config.py           # Settings (edit here)
├── ai/                 # AI orchestration
│   ├── model_registry.py
│   ├── ai_orchestrator.py
│   ├── ai_filter.py
│   ├── relevance.py
│   └── ollama_client.py
├── scraper/            # Scraping engines
├── server/             # API routes
└── utils/              # Helpers
```

---

Last Updated: May 2026 | AI Orchestrator: ✅ Ready
