# MarketSpy AI

**Mencari barang terbaik sesuai budget.**

MarketSpy AI adalah aplikasi scraping marketplace yang menggunakan teknologi Puppeteer, Selenium, dan AI lokal (Ollama) untuk menemukan produk terbaik sesuai dengan kriteria pencarian dan budget Anda.

## Fitur Utama

- **Scraping Multi-Engine**: Mendukung Puppeteer, Selenium, dan fallback otomatis
- **Filtering Cerdas**: Rule-based filtering dengan budget dan relevance checking
- **AI Orchestrator**: Validasi produk dengan model AI lokal (Ollama)
- **Kategorisasi Otomatis**: Produk dikelompokkan ke:
  - **Semua Barang**: Menampilkan semua produk yang valid
  - **Terbaik**: Produk dengan rating terbaik
  - **Termurah**: Produk dengan harga terendah
  - **Most Trusted**: Produk dengan reputasi toko terbaik
- **Feedback Learning**: Sistem pembelajaran dari feedback user untuk meningkatkan akurasi
- **UI Modern**: Interface midnight blue yang clean dan responsif

## Cara Install

### Prerequisites

- Python 3.9+
- Node.js 18+
- Ollama (opsional, untuk AI features)
- Browser: Chrome/Chromium atau Firefox

### Step 1: Install Dependencies

```bash
# Backend
pip install -r requirements.txt

# Frontend (sudah included di folder /web)
npm install
```

### Step 2: Setup Ollama (Opsional)

Untuk mengaktifkan AI Orchestrator, install Ollama dan model berikut:

```bash
ollama pull gemma3:4b      # Model classifier utama
ollama pull llama3.2:3b    # Model backup classifier
ollama pull phi4-mini      # Model JSON repair (optional)
ollama pull nomic-embed-text  # Model embedding untuk semantic search (optional)
```

Jika Ollama tidak tersedia, sistem akan tetap berjalan dengan rule-based filtering.

### Step 3: Konfigurasi

Edit `src/config.py` untuk konfigurasi:

```python
# Budget filter tolerance
DEFAULT_BUDGET_TOLERANCE = 20  # 20% tolerance

# AI settings
AI_ENABLE_CLASSIFIER = True
AI_ENABLE_SEMANTIC = True
AI_MODEL_CLASSIFIER = "gemma3:4b"
AI_MODEL_SEMANTIC = "nomic-embed-text"

# Scraper settings
PUPPETEER_TIMEOUT = 30000  # milliseconds
SELENIUM_TIMEOUT = 30  # seconds
```

## Cara Menjalankan

### Development Mode

```bash
# Terminal 1: Backend
python app.py

# Terminal 2: Frontend (optional, sudah serving dari backend)
# Buka http://localhost:8000 di browser
```

### Production Mode

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Cara Kerja Scraping

1. **Search Initiation**: User masuk query, target count, dan budget
2. **Engine Selection**: Sistem memilih engine (Puppeteer/Selenium) atau auto-fallback
3. **Page Navigation**: Browser membuka halaman marketplace (Tokopedia)
4. **Data Extraction**: Mengambil data produk (judul, harga, rating, gambar, etc)
5. **Deduplication**: Membersihkan produk duplikat
6. **Budget Filtering**: Filter produk berdasarkan harga dan budget tolerance
7. **Semantic Check**: Cek relevansi semantic (jika AI enabled)
8. **AI Validation**: Orchestrator AI menvalidasi produk borderline
9. **Ranking**: Menyusun rekomendasi berdasarkan kategori
10. **Result Display**: Tampilkan hasil ke UI

## Feedback Benar/Salah

Setelah scraping selesai, user bisa memberikan feedback untuk setiap produk:

- **Benar**: Produk sesuai dengan pencarian
- **Salah**: Produk tidak sesuai (dengan alasan)

Feedback disimpan dalam database dan digunakan untuk:
- Melatih model AI agar lebih akurat
- Menyesuaikan rule filter
- Meningkatkan scoring produk

### Data Feedback Disimpan

```json
{
  "search_id": "xxx",
  "product_id": "xxx",
  "user_action": "benar|salah",
  "selected_reasons": ["Alasan 1", "Alasan 2"],
  "note": "Catatan user",
  "ai_confidence": 0.95,
  "model_used": "gemma3:4b",
  "timestamp": "2024-xx-xx"
}
```

## Penjelasan Kategori

### Semua Barang
Menampilkan **semua produk** yang valid sesuai kriteria filter (budget, relevance, etc). Tidak ada limit jumlah.

### Terbaik
Produk **top-ranked** berdasarkan kombinasi:
- Rating tinggi
- Banyak review
- Harga kompetitif
- AI confidence tinggi

Limit jumlah sesuai input user di "Jumlah data per kategori".

### Termurah
Produk dengan **harga terendah** yang valid.
Limit jumlah sesuai input user.

### Most Trusted
Produk dari **toko terpercaya** dengan:
- Rating toko tinggi
- Banyak transaksi
- Respon time bagus

Limit jumlah sesuai input user.

## Form Input Penjelasan

| Field | Tipe | Wajib | Keterangan |
|-------|------|-------|-----------|
| Produk yang dicari | Text | Ya | Contoh: "laptop gaming" |
| Jumlah target | Number | Ya | Berapa produk yang ingin ditemukan (min 1, maks 100) |
| Toleransi budget | Number | Tidak | Persentase tolerance dari budget (0-100%, default 20%) |
| Budget | Currency | Tidak | Maksimal budget dalam Rupiah (opsional) |
| Jumlah data per kategori | Number | Tidak | Limit produk untuk kategori Terbaik/Termurah/Most Trusted (default 10) |
| Gunakan AI Orchestrator | Checkbox | Tidak | Aktifkan validation AI (jika Ollama available) |

## API Endpoints

### POST /api/search
Mulai search/scraping

```json
{
  "query": "laptop gaming",
  "target": 20,
  "budget": 10000000,
  "tolerance": 20,
  "ai": true,
  "use_ai": true,
  "category_limit": 10
}
```

### GET /api/progress/{search_id}
Get progress scraping

Response:
```json
{
  "stage": "scraping",
  "progress_percent": 45,
  "done": false,
  "found": 15,
  "valid": 12,
  "message": "Mengambil data produk..."
}
```

### GET /api/result/{search_id}
Get hasil akhir scraping

### POST /api/feedback
Send user feedback untuk produk

```json
{
  "search_id": "xxx",
  "product_id": "xxx",
  "user_action": "benar",
  "selected_reasons": [],
  "note": ""
}
```

## Troubleshooting

### "Ollama belum bisa dihubungi"
- Pastikan Ollama sudah running: `ollama serve`
- Check port Ollama (default 11434)
- Install model yang diperlukan: `ollama pull gemma3:4b`

### "Scraping timeout"
- Marketplace website mungkin slow
- Try increase timeout di config
- Check internet connection

### "Produk tidak ada"
- Query terlalu spesifik atau tidak ada di marketplace
- Try dengan query lebih umum
- Check target count tidak terlalu tinggi

### "Budget filter terlalu ketat"
- Increase tolerance percentage
- Atau tingkatkan budget amount
- Check kategori "Semua Barang" untuk melihat semua produk

## Development

### Project Structure

```
├── app.py                 # Main FastAPI app
├── src/
│   ├── config.py         # Configuration
│   ├── ai/               # AI orchestrator
│   ├── scraper/          # Scraper engines
│   ├── server/           # API endpoints
│   └── utils/            # Helper functions
├── web/                  # Frontend files
│   ├── index.html
│   ├── app.js
│   └── style.css
├── data/                 # Data storage
│   ├── ai_memory/        # AI learning data
│   └── feedback/         # User feedback logs
└── tests/                # Test files
```

### Running Tests

```bash
pytest tests/ -v
```

### Code Style

- Backend: PEP 8
- Frontend: Prettier + ESLint

## Tips Penggunaan

1. **Mulai dengan query umum**: "laptop" lebih baik daripada "laptop gaming ROG RTX 4090"
2. **Set target count wajar**: 20-50 adalah sweet spot
3. **Use budget jika tahu**: Feedback akan lebih akurat
4. **Check AI Orchestrator status**: Lihat di form apakah model tersedia
5. **Review hasil dengan teliti**: Feedback membantu AI belajar
6. **Gunakan kategori berbeda**: Coba Terbaik, Termurah, Most Trusted untuk perspektif berbeda

## License

MIT

## Support

Issues? Check GitHub issues atau contact developer.

---

**MarketSpy AI** - Mencari barang terbaik sesuai budget dengan teknologi AI lokal.
