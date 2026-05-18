# Development Guide

This document provides guidance for developers working on MarketSpy AI.

## Project Structure

```
PI V3/Draft Kode 2 - Gemini/
├── app.py                              # Flask entry point
├── requirements.txt                    # Python dependencies
├── test_scraper.py                     # Unit tests (pytest)
├── README.md                           # User documentation
├── DEVELOPMENT.md                      # This file
├── .env.example                        # Configuration template
│
├── scraper/
│   ├── __init__.py
│   └── tokopedia_scraper.py           # Tokopedia web scraper
│
├── ai_analyzer/
│   ├── __init__.py
│   └── product_analyzer.py            # Ollama LLM integration
│
└── templates/
    └── index.html                     # Frontend dashboard
```

## Code Architecture

### Data Flow

```
User Browser (index.html)
    ↓
POST /api/search
    ↓
app.py (Flask server)
    ├─→ TokopediaScraper.search()
    │   ├─→ Launch Playwright browser
    │   ├─→ Navigate to Tokopedia search
    │   ├─→ Extract products via JavaScript
    │   ├─→ Filter and deduplicate
    │   └─→ Return List[Dict]
    │
    └─→ ProductAIAnalyzer.analyze()
        ├─→ Check Ollama health
        ├─→ Batch products
        ├─→ Call Ollama API
        ├─→ Parse JSON response
        └─→ Return List[AnalysisResult]
    ↓
Return JSON response
    ↓
Frontend renders results
```

## Key Components

### 1. TokopediaScraper (scraper/tokopedia_scraper.py)

**Responsibilities:**
- Automate browser to navigate Tokopedia
- Extract product data from page DOM
- Filter results based on keyword and price
- Handle retries and errors

**Key Methods:**
- `search(keyword, max_halaman, min_rating)` - Main entry point
- `_do_search()` - Internal implementation with cleanup
- `to_dict_list()` - Return results as dict list

**Important Logic:**
```python
# Keyword filtering: Remove search term from accessory blocklist
search_terms = set(w.lower() for w in keyword.split() if len(w) > 2)
negative_keywords = [kw for kw in negative_keywords if kw not in search_terms]

# Price validation: Premium items require higher minimum
harga_wajar = item['harga'] >= 100000 if premium_term else item['harga'] >= 5000

# Deduplication: Track seen URLs in set
if item['url'] not in unique_urls:
    unique_urls.add(item['url'])
    self.results.append(item)
```

### 2. ProductAIAnalyzer (ai_analyzer/product_analyzer.py)

**Responsibilities:**
- Check Ollama health before analysis
- Batch products for efficiency
- Send evaluation prompt to Ollama
- Parse and validate AI responses

**Key Methods:**
- `analyze()` - Main entry point
- `_check_ollama_health()` - Verify Ollama is running
- `_build_analysis_prompt()` - Create evaluation prompt
- `_call_ollama()` - HTTP POST to Ollama
- `_parse_ai_response()` - Extract JSON from response

**AnalysisResult Fields:**
```python
@dataclass
class AnalysisResult:
    nama_produk: str           # Product name
    harga: int                 # Price in IDR
    harga_display: str         # Formatted price "Rp X.XXX.XXX"
    trust_score: float         # 0-100 (shop rating + sales)
    trust_label: str           # "Terpercaya", "Ragu-ragu", etc
    skor_value: float          # 0-100 (price-value ratio)
    rekomendasi: str           # "DIREKOMENDASIKAN" or "TIDAK DIREKOMENDASIKAN"
    catatan_ai: str            # AI commentary
```

### 3. Flask API (app.py)

**Endpoints:**
- `GET /` - Serve dashboard
- `POST /api/search` - Search and analyze

**Request:**
```json
{
  "keyword": "Mouse Gaming Razer",
  "banned_items": ["Wireless Charging Case"]
}
```

**Response:**
```json
{
  "status": "success|error",
  "data": [...] or "message": "error description"
}
```

## Development Workflow

### 1. Setting Up Development Environment

```bash
# Clone/enter project
cd "PI V3/Draft Kode 2 - Gemini"

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install browser drivers
playwright install
```

### 2. Running Tests

```bash
# Run all tests
pytest test_scraper.py -v

# Run specific test class
pytest test_scraper.py::TestScraperKeywordFiltering -v

# Run with coverage
pytest test_scraper.py --cov=scraper --cov-report=html
```

### 3. Making Changes

**Before modifying scraper logic:**
1. Write test for the change
2. Verify test fails (red)
3. Implement fix
4. Verify test passes (green)
5. Run full test suite

**Example: Adding new filter**
```python
# 1. Test first (test_scraper.py)
def test_filter_expensive_products(self):
    # Test that products > 10M are filtered
    pass

# 2. Implement (tokopedia_scraper.py)
if item['harga'] > 10000000:
    continue

# 3. Run test
pytest test_scraper.py::TestScraperKeywordFiltering::test_filter_expensive_products -v
```

### 4. Debugging Scraper

Enable headless=False to see browser window:
```python
scraper = TokopediaScraper(headless=False)
```

Check logs for detailed output:
```
[SCRAPER] Membuka URL (Filter: Paling Sesuai)...
[SCRAPER] Menggulir Halaman (Paling Sesuai)...
[SCRAPER] Ekstraksi Data (Paling Sesuai)...
[SCRAPER] Selesai Filter Paling Sesuai. Total terkumpul sejauh ini: 55 produk.
```

### 5. Testing AI Integration

Ensure Ollama is running:
```bash
# Terminal 1
ollama serve

# Terminal 2
python app.py
```

Test via API:
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"keyword": "Mouse Gaming"}'
```

## Common Issues & Solutions

### Issue: Captcha Blocking
**Symptoms:** "Browser mungkin terkena Captcha" error

**Solutions:**
1. Wait 10+ minutes before retrying
2. Switch network/VPN
3. Increase scroll delays in scraper
4. Use proxy rotation

**Code fix:**
```python
# Increase delay between scrolls
await page.wait_for_timeout(random.randint(1000, 2000))  # Was 600-1000
```

### Issue: DOM Selectors Not Working
**Symptoms:** No products extracted, all items get "Produk Tokopedia"

**Solutions:**
1. Tokopedia changed HTML structure
2. Add new selector to querySelector
3. Fallback logic uses longest text node

**Debug:**
```python
# Run in browser console
document.querySelectorAll('[data-testid="spnSRPProdName"]')
// Check if elements found
```

### Issue: Ollama Connection Refused
**Symptoms:** "Ollama tidak aktif"

**Solutions:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve

# Check available models
ollama list

# Pull if needed
ollama pull llama3.2
```

## Performance Optimization

### Reduce Scraping Time
1. Decrease max_halaman (default: 2)
2. Skip non-headless mode (headless=True)
3. Reduce scroll iterations

```python
# Edit in app.py
scraped_data = asyncio.run(scraper.search(keyword, max_halaman=1))  # Was 2
```

### Reduce AI Analysis Time
1. Use faster model
```bash
ollama pull mistral  # Faster than llama3.2
```

2. Reduce batch size
```python
analyzed_data = asyncio.run(analyzer.analyze(
    scraped_data, 
    batch_size=5,   # Was 10
    limit=5         # Was 10
))
```

## Testing Checklist

- [ ] Mousepad search returns mousepad products
- [ ] Mouse Gaming Razer search returns gaming mice
- [ ] Searches with 0 results return proper error
- [ ] Captcha error has helpful message
- [ ] Premium items (mouse/razer/headset) require 100k minimum
- [ ] Accessories (grip/case) are filtered out
- [ ] Products are deduplicated correctly
- [ ] AI analysis scores are reasonable (0-100)

## Deployment Considerations

1. **Headless Mode**: Always use `headless=True` in production
2. **Proxy Support**: Not currently implemented - consider adding for scale
3. **Rate Limiting**: Add delays between searches
4. **Error Recovery**: Test failure scenarios thoroughly
5. **Logging**: Use logging module, not print statements
6. **Secrets**: Never commit .env files with real credentials

## Contributing Guidelines

1. **Code Style**
   - Use type hints: `def search(keyword: str) -> List[Dict]:`
   - Follow PEP 8
   - Add docstrings to functions

2. **Commit Messages**
   ```
   [FEATURE] Add X feature
   [FIX] Fix X bug
   [REFACTOR] Improve X logic
   [TEST] Add tests for X
   [DOCS] Update X documentation
   ```

3. **Pull Request**
   - Write clear description
   - Reference related issues
   - Include test coverage
   - Update README if needed

## Useful References

- **Playwright Docs**: https://playwright.dev/python/
- **pytest Docs**: https://docs.pytest.org/
- **Flask Docs**: https://flask.palletsprojects.com/
- **Ollama Docs**: https://ollama.ai/library
- **Tokopedia**: https://www.tokopedia.com/

## Quick Commands

```bash
# Run application
python app.py

# Run tests
pytest test_scraper.py -v

# Run specific test
pytest test_scraper.py::TestName::test_method -v

# Install new package
pip install package_name

# Freeze dependencies
pip freeze > requirements.txt

# Clean cache
rm -rf .pytest_cache __pycache__ .venv
```
