# MarketSpy AI - Tokopedia Scraper & AI Analyzer

A Python application that scrapes product data from Tokopedia marketplace and analyzes it using local Ollama LLM.

## ✨ What's New

**AI Learning System** - The AI now learns from corrections and prevents repeating mistakes!

- 📚 Records all incorrect AI analyses
- 🔄 Prevents same mistakes from happening again
- ⚠️ Warns users when analyzing problematic products
- 📊 Tracks error patterns and statistics
- 🎯 Continuously improves without retraining

See [AI_LEARNING.md](AI_LEARNING.md) for complete documentation.

## Architecture

```
app.py                  # Flask server (port 5000)
├── /api/search         # POST endpoint for product search
│   ├── [TokopediaScraper] → Fetch products from Tokopedia
│   └── [ProductAIAnalyzer] → Analyze with Ollama LLM
└── /                   # Dashboard UI
    └── templates/index.html

Scraper Flow:
1. Navigate to Tokopedia search URL (3 filter variations: Relevant, Most Reviews, Cheapest)
2. Scroll page to trigger lazy loading
3. Extract product data via JavaScript
4. Filter results (keyword matching, price validation, exclude accessories)
5. Deduplicate products
6. Cleanup temporary browser cache

AI Analysis Flow:
1. Group products into batches
2. Send to Ollama with evaluation prompt
3. Parse JSON response
4. Return structured analysis (trust score, value score, recommendation)
```

## Installation

### Prerequisites
- Python 3.8+
- Ollama (https://ollama.com/download)
- Chrome/Chromium browser (for Playwright)

### Setup

```bash
# 1. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Playwright browsers
playwright install

# 4. Install Ollama and pull a model (in separate terminal)
ollama pull llama3.2  # Recommended - good balance
# OR
ollama pull mistral   # Better for JSON output
```

## Running the Application

### Terminal 1: Start Ollama Server
```bash
ollama serve
# Expected output: "Listening on 127.0.0.1:11434"
```

### Terminal 2: Start Flask Application
```bash
cd "PI V3/Draft Kode 2 - Gemini"
source .venv/bin/activate
python app.py
```

Application will be available at:
- http://localhost:5000 (local machine)
- http://192.168.18.114:5000 (network access)

## Usage

### Web Interface
1. Open http://localhost:5000 in browser
2. Enter search keyword (e.g., "Mouse Gaming Razer")
3. Click "Cari" (Search)
4. View results with AI analysis scores
5. Use filter buttons to sort: Best Value, Most Trusted, Price, Rating
6. Click product card to visit Tokopedia page

### API Endpoint

**POST /api/search**

Request:
```json
{
  "keyword": "Mouse Gaming Razer",
  "banned_items": ["Wireless Charging Case", "RGB Controller"]
}
```

Response:
```json
{
  "status": "success",
  "data": [
    {
      "nama_produk": "Razer DeathAdder V3 Pro Wired Gaming Mouse",
      "harga": 2500000,
      "harga_display": "Rp 2.500.000",
      "nama_toko": "Razer Official Store",
      "trust_score": 95.0,
      "trust_label": "Terpercaya",
      "skor_value": 88.0,
      "rekomendasi": "DIREKOMENDASIKAN",
      "rating_toko": 4.8,
      "terjual": "1.2rb",
      "url_produk": "https://...",
      "url_gambar": "https://..."
    }
  ]
}
```

Error Response:
```json
{
  "status": "error",
  "message": "Tidak ada produk ditemukan. Coba keyword lain atau periksa ejaan."
}
```

## Configuration

### Environment Variables (.env file)

```bash
# Optional: Override default Ollama settings
OLLAMA_MODEL=llama3.2
OLLAMA_URL=http://localhost:11434/api/generate
```

### Scraper Settings

Edit `scraper/tokopedia_scraper.py`:
- `MAX_RETRIES = 3` - Number of retry attempts
- `RETRY_DELAY = 2` - Seconds between retries
- `max_halaman = 2` - Number of Tokopedia sort filters to check
- `negative_keywords` - Accessory keywords to exclude

## Features

### Smart Keyword Filtering
- Removes search term from accessory blocklist (e.g., searching "Mousepad" won't filter mousepad products)
- Flexible keyword matching - ensures search terms appear in product titles
- Reasonable price validation - high-end items require minimum price threshold

### Retry Mechanism
- Automatic retry on failure (configurable attempts)
- Progressive delay between retries
- Graceful error messages for different failure modes

### Anti-Detection Measures
- Browser automation with Stealth plugin
- Random scroll timing to mimic human behavior
- Real Chrome user-agent
- Webdriver property obfuscation

### AI Analysis
- Trust Score (0-100): Based on shop rating and sales volume
- Value Score (0-100): Based on price relativity to product quality
- Custom product filtering via "banned items" list
- Batch processing for efficiency

## Troubleshooting

### Error: "Ollama tidak aktif"
```
Solution: Run "ollama serve" in a separate terminal
```

### Error: "Browser mungkin terkena Captcha"
```
Cause: Tokopedia detected automated access
Solutions:
1. Wait 5-10 minutes before trying again
2. Switch network/IP address
3. Try searching with different keyword
4. Increase scroll delays in scraper settings
```

### Error: "Tidak ada produk ditemukan"
```
Causes & Solutions:
1. Product doesn't exist on Tokopedia → Try different keyword
2. Keyword too specific → Use broader search terms
3. Typo in keyword → Check spelling
4. Product filtered by logic → Adjust negative_keywords
```

### Slow Performance
```
Causes:
1. Ollama running on limited hardware
2. Network latency to Tokopedia
3. Too many products being analyzed

Solutions:
1. Use smaller model: ollama pull phi3
2. Reduce max_halaman or limit in analyzer
3. Add more filters to narrow results
```

## Testing

Run the test suite:
```bash
pytest test_scraper.py -v
```

Tests cover:
- Keyword filtering logic
- Price validation
- Accessory exclusion
- Retry mechanism
- Error handling

## File Structure

```
├── app.py                              # Flask application
├── requirements.txt                    # Python dependencies
├── test_scraper.py                     # Scraper unit tests (9 tests)
├── test_ai_learning.py                 # AI learning tests (15 tests)
├── scraper/
│   ├── __init__.py
│   └── tokopedia_scraper.py           # Tokopedia web scraper
├── ai_analyzer/
│   ├── __init__.py
│   ├── product_analyzer.py            # Ollama LLM integration
│   └── mistake_tracker.py             # AI Learning System (NEW)
├── ai_learning_data/                   # AI learning storage
│   ├── mistakes.jsonl                 # Recorded AI mistakes
│   ├── patterns.json                  # Error pattern analysis
│   └── corrections.jsonl              # Pre-verified corrections
├── templates/
│   └── index.html                     # Dashboard UI
├── docs/
│   ├── README.md                      # This file
│   ├── AI_LEARNING.md                 # Complete learning system docs
│   ├── AI_LEARNING_QUICKSTART.md      # Quick start guide
│   ├── DEVELOPMENT.md                 # Developer guide
│   ├── QUICKSTART.md                  # 5-minute setup
│   ├── CHANGELOG.md                   # Version history
│   └── FIX_SUMMARY.md                 # What was fixed
└── .env.example                       # Configuration template
```

## Performance Notes

- First search: ~30-60 seconds (browser startup + Tokopedia loading)
- Subsequent searches: ~20-45 seconds (cache reuse + Ollama speed varies)
- Scraping: ~15-30 seconds per filter variant
- AI Analysis: ~10-15 seconds per batch
- Network speed significantly impacts performance

## API Rate Limiting

Tokopedia may rate-limit or CAPTCHA excessive requests:
- Wait 60+ seconds between searches from same IP
- Vary search keywords
- Use headless=False to debug browser behavior
- Consider proxy rotation for production use

## Known Limitations

1. **Captcha Protection**: Tokopedia periodically challenges automated access
2. **DOM Changes**: Tokopedia updates page structure frequently, may require selector updates
3. **Limited to Tokopedia**: Only scrapes Tokopedia marketplace
4. **Local LLM Only**: Requires running Ollama locally (no cloud API)
5. **Single-threaded**: Processes one search request at a time

## Future Improvements

- [ ] Proxy rotation support
- [ ] Multi-marketplace scraping (Shopee, Lazada)
- [ ] Result caching
- [ ] Scheduled background scraping
- [ ] Advanced filtering UI
- [ ] Export to CSV/Excel
- [ ] Price history tracking
- [ ] Real-time price alerts

## License

Educational project - Universitas Gunadarma 2025

## Support

For issues or questions:
1. Check Troubleshooting section above
2. Review console logs for error messages
3. Ensure Ollama is running with `ollama serve`
4. Verify Python environment is activated
