# MarketSpy AI

Local Tokopedia marketplace scraper with Puppeteer, Selenium fallback, budget filtering, feedback learning, and a local Ollama AI Orchestrator.

## Quick Start

```bash
python -m pip install -r requirements.txt
npm install
python app.py
```

Open http://127.0.0.1:3000.

## Supported Ollama Models

Only these models are supported:

- `gemma3:4b` - balanced classifier, highest priority
- `llama3.2:3b` - fast classifier fallback
- `phi4-mini` - JSON repair only
- `nomic-embed-text` - semantic scoring only

Model selection is automatic. The app detects installed models with `GET /api/tags`, and `:latest` tags such as `phi4-mini:latest` and `nomic-embed-text:latest` satisfy their supported base names. Unsupported legacy large classifier models were removed and are ignored.

## AI Orchestrator Behavior

The active search pipeline is:

```text
scrape raw -> normalize -> dedupe -> budget filter -> rules -> AI borderline check -> fallback expansion -> rank
```

Rules handle obvious accepts and rejects first. Ollama `POST /api/chat` is called only for borderline products when AI is enabled and a supported classifier is installed. If no AI model is available, deterministic rules and fallback expansion still work.

If `ai_checked` is `0`, result metadata includes one exact `ai_skip_reason`:

- `AI disabled`
- `No supported classifier installed`
- `No borderline candidates`
- `All products handled by rules`
- `Candidate pool empty`

If AI is enabled, a classifier is installed, and `borderline_candidates > 0`, backend logs should include `POST /api/chat` and `ai_calls_attempted > 0`.

## Result Count Behavior

Filtering runs only on the candidate pool:

- With budget enabled, the candidate pool is budget-valid products.
- With budget disabled, the candidate pool is deduped products.
- If accepted products are below the requested count, fallback expansion fills from safe low-confidence candidates.
- Obvious junk is still rejected.

When fallback expansion is used, the response warning is:

```text
Beberapa produk confidence rendah ditambahkan agar mendekati target. Produk obvious junk tetap dibuang.
```

If the app still cannot reach the target, the warning explains how many safe products were available from the valid candidate pool.

## Images

Scrapers extract images from `currentSrc`, `src`, `data-src`, `data-original`, `srcset`, `picture img`, and `source[srcset]`. Invalid values such as empty strings, data URLs, base64, SVGs, undefined/null markers, and raw missing-image labels are rejected.

The frontend creates image DOM nodes safely. It renders the marketplace image when a valid URL exists, and shows an Indonesian placeholder only when the image is missing or fails to load.

If more than 70% of extracted products are missing images, debug JSON is written. Puppeteer and Selenium also save image-missing HTML and screenshots when the browser page is still available.

## UI Controls

- `Terbaik` sorts current results by confidence, rating, sold count, then price.
- `Termurah` sorts current results by price ascending.
- `Most Trusted` sorts current results by store trust, rating, sold count, and review count.

Quick sort buttons sort the current products in the browser. They do not rescrape and do not call AI.

Engine Comparison appears only when engine mode is `Compare both` (`compare_both`). It is hidden for Auto, Puppeteer only, and Selenium only.

## API

```http
GET /api/ai/status
POST /api/search
GET /api/progress/{search_id}
GET /api/result/{search_id}
POST /api/feedback
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

## Troubleshooting

### AI Accepted is 0

1. Call `/api/ai/status`.
2. Confirm `classifier` is `gemma3:4b` or `llama3.2:3b`.
3. Check `result_metadata.ai_skip_reason`.
4. If `borderline_candidates > 0`, confirm logs show `POST /api/chat`.

### Displayed is much lower than requested

Check `requested`, `budget_valid`, `candidate_pool`, `rule_accepted`, `ai_checked`, `fallback_added`, `displayed`, and `limited_reason` in `result_metadata`.

### Product images are missing

Check `images_extracted_count` and `images_missing_count` in logs/debug files. Placeholders mean no valid marketplace image URL was extracted or the browser rejected the image load.

## Tests

```bash
python -m pytest tests/ -v
```
