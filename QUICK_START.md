# Quick Start Guide

## 1️⃣ Install & Setup (5 minutes)

```bash
cd "c:\Users\Farras\PI V3\RB-C1"

# Install Python packages
python -m pip install -r requirements.txt

# Install Node packages
npm install

# Start Ollama (separate terminal)
ollama pull gemma3:4b
ollama pull llama3.2:3b
ollama pull phi4-mini
ollama pull nomic-embed-text
ollama serve
```

## 2️⃣ Run the App

```bash
python app.py
```

Open browser: **http://127.0.0.1:3000**

## 3️⃣ Verify Everything Works

### Option A: Via Web UI
1. Type "laptop gaming" in search box
2. Select engine mode: **Auto** (try Puppeteer, fallback to Rollback)
3. Click **Mulai Scraping**
4. Wait for results (~2-3 minutes)

### Option B: Via Test Endpoint
```bash
# Test Puppeteer preflight
curl "http://127.0.0.1:3000/api/preflight/puppeteer?query=laptop"

# Test Rollback preflight
curl "http://127.0.0.1:3000/api/preflight/rollback?query=laptop"
```

### Option C: Run Automated Tests
```bash
python -m pytest tests/ -v
# Should show: 58 passed in ~0.7s
```

## 🎯 Common Scenarios

### Scenario 1: Both Engines Work
1. Choose mode: **Compare both**
2. See results from Puppeteer AND Rollback
3. Pick which you prefer
✅ **Works when**: Network is stable, Chrome loads normally

### Scenario 2: Puppeteer Gets HTTP/2 Error
1. App tries Puppeteer → fails with ERR_HTTP2_PROTOCOL_ERROR
2. Auto mode → switches to Rollback automatically
3. Shows: "Browser membuka Chrome error page: http2_protocol_error"
✅ **Works when**: Rollback (Selenium) succeeds

### Scenario 3: Qwen Fails
1. Products scraped successfully (raw=42)
2. Budget filters applied (budget=35)
3. Qwen server timeout or 500
4. Results shown with fallback scoring
5. Warning: "Qwen gagal, hasil raw/budget tetap ditampilkan"
✅ **Works when**: Ollama is down or model loading

### Scenario 4: Learn from Feedback
1. See wrong product (e.g., mouse listed as laptop)
2. Click **Ajarkan AI**
3. Select categories: [mouse, not_laptop, should_exclude]
4. Add note: "This is a mouse, not a laptop"
5. Click Save
6. Next search: AI will filter mouse better
✅ **Works when**: Feedback is saved to feedback.jsonl

## 🔧 Configuration

### AI Toggle
- **ON**: Use Qwen for relevance filtering
- **OFF**: Use fallback scoring (no Ollama needed)

### Engine Mode
- **Auto**: Try Puppeteer first, fallback to Rollback
- **Puppeteer only**: Puppeteer or fail
- **Rollback only**: Selenium or fail
- **Compare both**: Run both, show side-by-side

### Budget
- Leave empty: No budget filtering
- Enter amount: Filter to Rp ± tolerance%
- E.g., "10 juta" ±20% = Rp 8jt to Rp 12jt

## 📊 Monitoring

### Check Search Status
```bash
# Get progress in real-time
curl http://127.0.0.1:3000/api/progress/{search_id}
```

### Check Final Results
```bash
curl http://127.0.0.1:3000/api/result/{search_id}
```

### View Debug Files
```bash
# Browser error diagnostic
data/debug/{search_id}/puppeteer_preflight_failed.json

# Qwen failure details
data/debug/{search_id}/qwen_error.json

# Budget filter analysis
data/debug/{search_id}/budget_filter_debug_rollback.json
```

## 🚨 Emergency Fixes

### "Can't reach http://127.0.0.1:3000"
```bash
# Check if server is running
ps aux | grep python

# Restart server
python app.py
```

### "No products found / raw=0"
1. Check preflight: `GET /api/preflight/puppeteer?query=test`
2. Look for `opened_real_page: false` + `error_type`
3. Common fixes:
   - Check internet connection
   - Check Tokopedia.com is accessible
   - Restart browser/Puppeteer cache: Remove `node_modules/.puppeteer-cache`

### "Qwen not responding"
```bash
# Check Ollama
curl http://localhost:11434/api/tags

# If empty, pull model
ollama pull gemma3:4b

# If slow, check GPU
nvidia-smi  # On NVIDIA
```

### "Reset everything and start fresh"
```bash
# Clear AI learning
curl -X POST http://127.0.0.1:3000/api/ai/reset

# Clear debug files
rm -r data/debug/*

# Restart server
python app.py
```

## ✅ Success Indicators

- [ ] `python app.py` starts without errors
- [ ] Web UI loads at http://127.0.0.1:3000
- [ ] Can type in search box
- [ ] "Mulai Scraping" button works
- [ ] Progress bar appears
- [ ] Results show in 2-3 minutes
- [ ] Feedback buttons present on products
- [ ] "Ajarkan AI" button opens modal
- [ ] All tests pass: `pytest tests/ -v`

## 📞 Support

- **Chrome error page?** → Check debug JSON in `data/debug/{search_id}/`
- **Qwen failing?** → Check `qwen_error.json` in same folder
- **Products dropped?** → Check `budget_filter_debug_{engine}.json`
- **Wrong results?** → Use "Ajarkan AI" to teach AI with examples

---

**Next**: See `IMPLEMENTATION_SUMMARY.md` for full architecture & troubleshooting
