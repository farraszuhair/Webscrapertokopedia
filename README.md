# PasarIntai AI

Local Tokopedia product scraper with Puppeteer, Selenium/rollback fallback, budget filtering, feedback learning, and a local Ollama AI orchestrator.

## How to Run

```bash
python -m pip install -r requirements.txt
npm install
python app.py
```

Open http://127.0.0.1:3000.

If port `3000` is busy:

```bash
PORT=3001 python app.py
```

On Windows PowerShell:

```powershell
$env:PORT=3001
python app.py
```

## Required Setup

- Python 3.11+ recommended.
- Node.js and `npm install` are required for the Puppeteer worker.
- Chrome or Chromium must be available for Puppeteer/Selenium scraping.
- Ollama is optional but required for local AI classification.

Install supported Ollama models:

```bash
ollama pull gemma3:4b
ollama pull llama3.2:3b
ollama pull phi4-mini
ollama pull nomic-embed-text
ollama serve
```

## AI Configuration

Supported models:

- `gemma3:4b` - default classifier.
- `llama3.2:3b` - fallback classifier.
- `phi4-mini` - JSON repair.
- `nomic-embed-text` - semantic scoring.

Useful environment variables:

```bash
AI_MODEL=gemma3:4b
AI_AUDIT_MAX_PRODUCTS=3
AI_BATCH_CLASSIFY=true
AI_BATCH_SIZE=3
AI_CHAT_TIMEOUT_SECONDS=75
AI_CHAT_NUM_CTX=4096
AI_CHAT_NUM_PREDICT=180
OLLAMA_MAX_CONCURRENT_REQUESTS=1
```

`AI_AUDIT_MAX_PRODUCTS` is intentionally conservative by default. On a local laptop, limiting the classifier audit batch protects CPU/RAM while rules, semantic scoring, and fallback expansion keep results useful. Raise it only if your machine can handle longer Ollama jobs.

## Storage

Feedback and learning data are local files/SQLite under `data/ai_memory` and `data/feedback`. Do not delete those folders if you want to keep user corrections.

Search results are kept in local process memory with a TTL and max-item cap:

```bash
RESULT_STORE_TTL_SECONDS=3600
RESULT_STORE_MAX_ITEMS=50
```

This means `/api/result/{search_id}` works after a search completes, but old results expire and all in-memory results disappear when the server restarts.

## API

```http
GET /api/ai/status
POST /api/search
GET /api/progress/{search_id}
GET /api/result/{search_id}
POST /api/feedback
GET /api/feedback/summary
```

Example search:

```json
{
  "query": "laptop gaming",
  "target_count": 50,
  "budget": "10000000",
  "tolerance": 20,
  "use_ai": true,
  "engine_mode": "auto",
  "sort_mode": "terbaik"
}
```

Feedback accepts both old and new field names:

- `reasons` or `selected_reasons`
- `note` or `custom_reason`

## Known Limitations

- Tokopedia pages can block, throttle, or change markup.
- Puppeteer/Selenium runs are network and browser dependent.
- Ollama on CPU can be slow; classifier calls are deliberately capped.
- Results are stored in memory with TTL, not in a durable search database.
- Feedback learning is local to this machine.

## Troubleshooting

### Ollama Timeout

If `result_metadata.ai_timeouts` increases or logs show `/api/chat` timing out:

1. Confirm Ollama is running: `ollama serve`.
2. Check status: `GET /api/ai/status`.
3. Keep `AI_AUDIT_MAX_PRODUCTS=3` on CPU-only machines.
4. Use `gemma3:4b` or `llama3.2:3b`, not a larger unsupported model.
5. Avoid running other heavy Ollama jobs during scraping.
6. If needed, increase `AI_CHAT_TIMEOUT_SECONDS`, but expect slower searches.

### Port 3000 Busy

Start on another port:

```bash
PORT=3001 python app.py
```

Or stop the process that is listening on port 3000 and rerun `python app.py`.

### Search Returns Too Few Products

Check `result_metadata` fields:

- `requested_count`
- `budget_valid_count`
- `candidate_pool`
- `rule_accepted`
- `classifier_checked`
- `fallback_added`
- `displayed_count`
- `limited_reason`

Raise budget tolerance, disable strict budget mode, or lower the requested count if the valid product pool is small.

### UI Does Not Update

The active frontend is served from:

- `web/index.html`
- `web/app.js`
- `web/style.css`
- `web/vendor/anime.min.js`

Hard refresh the browser. FastAPI sends no-cache headers for HTML/CSS/JS.

## Developer Utilities

The repo context packer lives at:

```bash
python tools/pack_repo_for_claude.py
```

It writes `_claude_upload/`, which is ignored by git and excluded from its own package output.

## Tests

```bash
python -m pytest tests/ -v
```
