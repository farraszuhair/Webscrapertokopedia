# Tokopedia Scraper

FastAPI Tokopedia scraper with two engines:

- Puppeteer worker (`src/scraper/puppeteer_worker.js`)
- Rollback/Selenium engine (`src/scraper/rollback_engine.py`)

Run command stays:

```bash
python app.py
```

## Install

```bash
python -m pip install -r requirements.txt
npm install
```

## Run

```bash
python app.py
```

Open:

```text
http://127.0.0.1:3000
```

## API Shape

```json
{
  "query": "laptop gaming",
  "target": 25,
  "budget": "10.000.000",
  "tolerance": 20,
  "ai": true,
  "engine_mode": "auto"
}
```

`engine_mode` values:

- `auto`
- `puppeteer`
- `rollback`
- `compare`

Empty budget disables budget filtering. It is not parsed as zero.

## Budget Debug

When budget rejects products, debug is written to:

```text
data/debug/<search_id>/budget_filter_debug.json
```

Compare mode writes per-engine files:

```text
data/debug/<search_id>/budget_filter_debug_puppeteer.json
data/debug/<search_id>/budget_filter_debug_rollback.json
```

## Tests

```bash
python -m pytest tests/test_currency.py tests/test_schema.py tests/test_app_import.py
```
