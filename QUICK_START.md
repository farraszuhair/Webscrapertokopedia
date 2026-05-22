# Quick Start Guide

## 1. Install and Setup

```bash
cd "c:\Users\Farras\PI V3\RB-C1"
python -m pip install -r requirements.txt
npm install
```

Start Ollama and install the supported local models:

```bash
ollama pull gemma3:4b
ollama pull llama3.2:3b
ollama pull phi4-mini
ollama pull nomic-embed-text
ollama serve
```

## 2. Run

```bash
python app.py
```

Open http://127.0.0.1:3000.

## 3. Verify

```bash
curl http://127.0.0.1:3000/api/ai/status
python -m pytest tests/ -v
```

## Common Modes

- Auto: try Puppeteer first, then Selenium fallback.
- Puppeteer only: run Puppeteer and fail if it cannot extract products.
- Selenium only: run the Selenium fallback engine.
- Compare both: run both engines and show Engine Comparison.

Engine Comparison is hidden unless Compare both is selected.

## AI Orchestrator

- Model selection is automatic.
- Installed models are detected from `GET /api/tags`.
- `POST /api/chat` is called only for borderline products.
- If no supported classifier is installed, deterministic rules and fallback expansion still work.
- `phi4-mini` is used only for malformed JSON repair.
- `nomic-embed-text` is used only for semantic scoring.

## Result Controls

- Terbaik sorts the current result list by confidence, rating, sold count, then price.
- Termurah sorts the current result list by price without rescraping.
- Most Trusted sorts the current result list by trust signals without rescraping.
- Product cards render marketplace images when valid URLs exist and show an Indonesian fallback only when images are missing or fail to load.

## Troubleshooting AI Accepted 0

Check `/api/ai/status` first. If `classifier` is missing, install `gemma3:4b` or `llama3.2:3b`.

If `ai_checked` is `0`, inspect `ai_skip_reason` in the result metadata:

- `AI disabled`
- `No supported classifier installed`
- `No borderline candidates`
- `All products handled by rules`
- `Candidate pool empty`

If AI is enabled, a classifier is installed, and `borderline_candidates > 0`, the backend logs should include `POST /api/chat` and `ai_calls_attempted > 0`.
