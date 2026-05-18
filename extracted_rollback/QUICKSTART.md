# Quick Start Guide

Get MarketSpy AI up and running in 5 minutes.

## Prerequisites
- Windows/Mac/Linux
- Python 3.8+
- 4GB RAM minimum
- Internet connection

## Step 1: Install Ollama (2 minutes)

### Windows
1. Download from https://ollama.com/download/windows
2. Run installer and follow prompts
3. Open PowerShell and verify:
   ```bash
   ollama --version
   ```

### Mac
```bash
brew install ollama
```

### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

## Step 2: Pull a Model (3 minutes)

Open terminal and run:
```bash
# Recommended: Balanced speed and quality
ollama pull llama3.2

# OR: Better JSON parsing (faster)
ollama pull mistral

# OR: Lightweight (< 4GB RAM)
ollama pull phi3
```

Wait for download to complete (1-3 GB).

## Step 3: Setup Python Project (2 minutes)

```bash
# Navigate to project
cd "PI V3/Draft Kode 2 - Gemini"

# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install browser drivers
playwright install
```

## Step 4: Start Application (2 minutes)

### Terminal 1: Start Ollama Server
```bash
ollama serve
# You should see: "Listening on 127.0.0.1:11434"
```

### Terminal 2: Start Flask Server
```bash
# Make sure you're in project directory and .venv is activated
python app.py

# You should see:
# * Running on http://127.0.0.1:5000
# * Running on http://192.168.18.114:5000
```

### Terminal 3: Open Browser
1. Go to http://localhost:5000
2. Type search query (e.g., "Mouse Gaming Razer")
3. Click "Cari" button
4. Wait for results...

## Done! 🎉

You're now using MarketSpy AI with local LLM analysis!

## Common Issues

### "Ollama tidak aktif"
Make sure Terminal 1 is still running `ollama serve`

### "Browser mungkin terkena Captcha"
Wait 10 minutes and try again with different keyword

### "Tidak ada produk ditemukan"
Try:
- Different spelling
- Broader search term (e.g., "mouse" instead of "wireless mouse")
- Check Tokopedia manually to see if product exists

### Slow Performance
If it's taking > 60 seconds:
1. Try smaller model: `ollama pull phi3`
2. Verify internet speed
3. Check system resources (RAM/CPU)

## Next Steps

- Read full [README.md](README.md) for advanced features
- Check [DEVELOPMENT.md](DEVELOPMENT.md) to contribute
- Explore filter buttons on dashboard
- Try different search keywords

## Files to Know

- `app.py` - Main application
- `scraper/tokopedia_scraper.py` - Scraper logic
- `ai_analyzer/product_analyzer.py` - LLM integration
- `templates/index.html` - Web interface

## Stop Application

Press `Ctrl+C` in each terminal window:
1. Flask server (Terminal 2)
2. Ollama server (Terminal 1)

## Troubleshooting

For detailed troubleshooting, see [README.md - Troubleshooting section](README.md#troubleshooting)

For developer setup, see [DEVELOPMENT.md](DEVELOPMENT.md)
