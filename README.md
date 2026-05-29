# PasarIntai AI - Sistem Scraping dan Rekomendasi Produk Marketplace

**PasarIntai AI** adalah aplikasi web terpadu yang menggabungkan teknologi scraping otomatis, filter budget cerdas, evaluasi semantik berbasis AI lokal, dan sistem pembelajaran feedback pengguna untuk memberikan pengalaman kurasi produk marketplace yang presisi dan responsif.

---

## 📋 Daftar Isi

1. [Deskripsi](#deskripsi)
2. [Fitur Utama](#fitur-utama)
3. [Struktur Project](#struktur-project)
4. [Cara Menjalankan](#cara-menjalankan)
5. [Konfigurasi AI Lokal](#konfigurasi-ai-lokal)
6. [Alur Kerja Sistem](#alur-kerja-sistem)
7. [Penjelasan Rekomendasi Cepat](#penjelasan-rekomendasi-cepat)
8. [Detail Produk dan Feedback](#detail-produk-dan-feedback)
9. [Troubleshooting](#troubleshooting)
10. [Catatan Pengembangan](#catatan-pengembangan)
11. [Batasan Sistem](#batasan-sistem)

---

## 🎯 Deskripsi

**PasarIntai AI** dirancang untuk memecahkan masalah kurasi produk di marketplace berskala besar. Sistem ini:
- Mengotomasi pengambilan data produk dari Tokopedia dengan presisi tinggi
- Menerapkan filter budget dinamis dengan toleransi persentase fleksibel
- Mengintegrasikan model bahasa lokal (Ollama) untuk evaluasi semantik tanpa biaya API
- Mempelajari preferensi pengguna melalui sistem feedback interaktif
- Menyajikan UI responsif midnight-blue premium dengan animasi smooth dan aksesibilitas penuh

Aplikasi ini dibangun dengan **FastAPI** (backend), **Anime.js** (animasi), dan **vanilla JavaScript** (frontend), mengutamakan performa lokal dan transparansi AI.

---

## ✨ Fitur Utama

### 🔍 Scraping Otomatis
- **Engine Dual**: Puppeteer (browser automation) dengan fallback otomatis ke Selenium
- **Parsing Terstruktur**: Ekstraksi data: judul, harga, rating, toko, lokasi, foto
- **Error Recovery**: Retry logic dan alternative routing jika satu engine gagal

### 💰 Filter Budget Cerdas
- **Batas Harga Elastis**: Set budget maksimal dengan toleransi persentase (default 20%)
- **Prioritas Fleksibel**: Pilih prioritas jumlah target vs. kepatuhan budget ketat

### 🧠 Evaluasi Semantik AI
- **Ollama Lokal**: Menggunakan model gemma3:4b untuk klasifikasi kelayakan tanpa internet
- **Batch Processing**: Proses hingga 3 produk per batch (configurable) untuk efisiensi RAM
- **Fallback Otomatis**: Jika Ollama timeout, sistem fallback ke rules berbasis keyword

### ⚡ Rekomendasi Cepat
Empat kategori filter instan:
- **Semua Barang**: Menampilkan seluruh produk hasil scrape
- **Terbaik**: Diurutkan berdasarkan skor kepercayaan AI tertinggi
- **Termurah**: Diurutkan dari harga terendah
- **Most Trusted**: Produk dengan rating tinggi dan jual banyak

### 📝 Feedback Interaktif
- **Benar/Salah Buttons**: Tandai kecocokan produk secara instan
- **Panel Alasan Dinamis**: Jika "Salah", buka panel untuk pilih alasan spesifik
- **Pembelajaran Sistem**: Feedback disimpan dan digunakan untuk training iteratif

### 📊 Progress Tracking Real-time
- **Timeline Scraping**: Tampilkan durasi aktif, jumlah crawled vs. target, dan ETA sisa
- **Status Wordmark Animasi**: Teks "Siap"/"Berjalan"/"Selesai"/"Error" di pojok kanan atas dengan animasi stroke SVG (bukan dot atau ring)

### 🎨 UI Premium Responsive
- **Midnight Blue Theme**: Palet warna gelap bergaya premium dengan kontras optimal
- **Responsive Grid**: Desktop (2 kolom), Tablet (stacked), Mobile (full-width)
- **Anime.js Transitions**: Category zoom, product fade, modal slide dengan motion profiles adaptive per viewport
- **Modal Dialog Utama**: Detail produk dengan grid image + content, scrollable dengan native scrollbar thin

### ✅ Produk Reviewed Auto-Filing
- **Checked Tray**: Produk yang sudah diberikan feedback langsung masuk ke kotak terpisah
- **Keep List Clean**: Daftar utama hanya tampilkan belum-direview agar UX tetap fokus

---

## 📁 Struktur Project

```
RB-C1/
├── app.py                          # Entry point FastAPI
├── requirements.txt                # Python dependencies
├── package.json                    # Node.js dependencies (Puppeteer)
├── pytest.ini                      # Test runner config
├── QUICK_START.md                  # Quick reference guide
├── README.md                       # Dokumentasi ini
├── SOURCE_REGISTER.md              # Register engine dan AI models
│
├── src/                            # Source code Python backend
│   ├── __init__.py
│   ├── config.py                   # Configuration loader (.env)
│   ├── ai/                         # AI orchestrator & models
│   ├── scraper/                    # Puppeteer & Selenium bindings
│   ├── server/                     # FastAPI routes & websockets
│   └── utils/                      # Helpers (currency, normalizer, etc)
│
├── web/                            # Frontend (vanilla JS + CSS)
│   ├── index.html                  # Main HTML with modal structure
│   ├── app.js                      # (~4000 lines) Main JS controller
│   ├── style.css                   # (~4000 lines) Responsive styling + animations
│   └── vendor/                     # Third-party: anime.min.js
│
├── tests/                          # Pytest test suite
│   ├── test_app_import.py
│   ├── test_integration.py
│   └── ... (10+ test files)
│
├── data/                           # Runtime data storage
│   ├── ai_memory/                  # AI learning cache (category_rules, feedback)
│   ├── debug/                      # Debug logs per session
│   └── feedback/                   # User feedback archive
│
└── tools/                          # Utility scripts
    └── pack_repo_for_claude.py    # Export codebase for AI context
```

---

## 🚀 Cara Menjalankan

### Prasyarat
- **Python 3.8+**
- **Node.js 18+** (untuk Puppeteer)
- **Ollama installed** (untuk AI lokal; opsional tapi recommended)

### 1. Setup & Instalasi

**Clone atau extract repo:**
```bash
cd RB-C1
```

**Instal Python dependencies:**
```bash
pip install -r requirements.txt
```

**Instal Node dependencies (untuk Puppeteer):**
```bash
npm install
```

### 2. Jalankan Aplikasi

**Start server:**
```bash
python app.py
```

Output yang diharapkan:
```
[OK] Python dependencies found.
[OK] Node ready: v22.14.0
[INFO] Starting FastAPI server on http://127.0.0.1:3000
INFO:     Application startup complete.
```

### 3. Akses di Browser

Buka: **[http://127.0.0.1:3000](http://127.0.0.1:3000)**

---

## ⚙️ Konfigurasi AI Lokal

### Prasyarat Ollama
Pastikan Ollama sudah running:
```bash
ollama serve
```
(Pada window/tab terminal terpisah)

### Install Model AI
Jalankan perintah ini sekali saja:
```bash
ollama pull gemma3:4b
ollama pull llama3.2:3b
ollama pull phi4-mini
ollama pull nomic-embed-text
```

### Environment Variables
Buat atau edit file `.env` di root project:

```env
# AI Configuration
AI_MODEL=gemma3:4b
AI_AUDIT_MAX_PRODUCTS=3
AI_BATCH_CLASSIFY=true
AI_BATCH_SIZE=3
AI_CHAT_TIMEOUT_SECONDS=75

# Scraper Configuration
PUPPETEER_HEADLESS=true
PUPPETEER_TIMEOUT=30000

# Server Configuration
PORT=3000
LOG_LEVEL=INFO
```

**Penjelasan:**
- `AI_MODEL`: Model utama untuk klasifikasi (gemma3:4b recommended)
- `AI_AUDIT_MAX_PRODUCTS`: Jumlah produk per batch ke AI (3 default, konservatif untuk RAM lokal)
- `AI_BATCH_CLASSIFY`: Enable batch classification untuk efisiensi
- `AI_CHAT_TIMEOUT_SECONDS`: Timeout Ollama response (75 detik, increase jika hardware lambat)
- `PUPPETEER_TIMEOUT`: Timeout browser navigation (30 detik)

> **⚠️ Note**: Nilai `AI_AUDIT_MAX_PRODUCTS=3` dipilih konservatif untuk melindungi laptop lokal. Jika menggunakan GPU/hardware powerful, bisa di-set ke 5-10.

---

## 🔄 Alur Kerja Sistem

### 1. User Input Search
User masukkan:
- Query produk (contoh: "laptop gaming")
- Target jumlah produk (default 50)
- Budget maksimal (Rp, opsional)
- Toleransi budget (%, default 20%)

### 2. Scraping Phase
- **Browser Launch**: Puppeteer/Selenium buka Tokopedia
- **Search & Crawl**: Iterasi halaman hasil search, scrape data
- **Fallback**: Jika Puppeteer fail, auto-switch ke Selenium

### 3. AI Evaluation
- **Batch Send**: Kirim produk ke Ollama dalam batch kecil
- **Semantic Check**: Model evaluasi: "Apakah produk ini sesuai query?"
- **Score Generate**: Sistem beri confidence score 0.0-1.0
- **Fallback Rules**: Jika Ollama timeout, gunakan regex/keyword rules

### 4. Recommendation Display
Tampilkan hasil di panel utama dengan:
- Grid product cards (image, title, price, meta, badges)
- Kategori filter: Semua/Terbaik/Termurah/Trusted
- Progress bar scraping + ETA timer

### 5. User Review & Feedback
- User klik product card → modal detail terbuka (zoom + fade animation)
- User klik "Benar" → sistem catat, pindah produk berikutnya
- User klik "Salah" → panel alasan muncul, pilih reason, submit
- Produk reviewed → masuk "Sudah Dicek" tray

### 6. Learning & Export
- Feedback disimpan di `data/ai_memory/feedback.jsonl`
- Sistem belajar pola feedback pengguna
- Hasil scrape bisa diexport (TODO: CSV/JSON export endpoint)

---

## 🎬 Penjelasan Rekomendasi Cepat

### Filter Buttons (Top of Panel)
Empat tombol kategori di bawah "Rekomendasi Produk":

#### 1. **Semua Barang**
- Menampilkan 100% produk hasil scrape
- Urutan: Sesuai hasil scrape (no sorting)
- Use case: Review keseluruhan produk tanpa filter

#### 2. **Terbaik**
- Filter & sort berdasarkan: `ai_confidence` score tertinggi
- Formula: Produk dengan confidence ≥ 0.8 diprioritaskan
- Urutan: Descending confidence score
- Use case: Lihat top recommendations berdasarkan AI

#### 3. **Termurah**
- Sort berdasarkan `price_value` (numeric harga)
- Urutan: Ascending (harga terendah di atas)
- Budget check: Tetap respek filter budget jika aktif
- Use case: Cari deal harga terbaik yang sesuai query

#### 4. **Most Trusted**
- Sort berdasarkan kombinasi: rating + sold count
- Formula: `(rating * 0.6) + (sold_count_normalized * 0.4)`
- Urutan: Score tertinggi di atas
- Use case: Pilih produk populer & terpercaya berdasarkan crowd voting

### Cara Menggunakan Filter
1. Tunggu hasil scrape selesai
2. Klik salah satu tombol kategori (Semua Barang, Terbaik, Termurah, Most Trusted)
3. UI melakukan transisi **camera zoom**: tombol yang diklik dikloning, bergerak ke tengah panel, membesar dengan glow, lalu produk baru muncul setelah zoom selesai
4. Hanya satu judul kategori utama yang tampil di kiri; tidak ada duplikasi teks kategori

### Transisi Camera Zoom (Bukan Tab Biasa)
Saat kategori diganti, sistem tidak sekadar mengganti kelas aktif pada tombol. Urutan animasi:
1. Produk lama memudar keluar
2. Clone tombol kategori muncul di posisi layar asli tombol
3. Clone bergerak ke pusat panel rekomendasi
4. Clone membesar (efek masuk ke kategori) disertai radial glow warna aksen kategori
5. Judul kategori diperbarui
6. Produk baru dirender dan masuk dengan stagger

Marker build UI: `UI_FINAL_CAMERA_ZOOM_CATEGORY_DRAWABLE_FIX_20260529`

---

## 📦 Detail Produk dan Feedback

### Modal Detail Produk
Klik kartu produk di panel Rekomendasi Cepat untuk membuka modal overlay (`.product-modal-backdrop`).

**Konten Modal:**
- **Media kiri / atas**: Gambar produk dengan placeholder `TIDAK ADA GAMBAR` jika URL kosong atau gagal dimuat
- **Konten kanan / bawah**: Judul (wrap aman), toko, harga Rupiah, meta (rating, terjual, keyakinan AI)
- **Tanpa scrollbar horizontal**: Lebar modal dibatasi `min(1280px, calc(100vw - 32px))`; semua anak memakai `min-width: 0`

### Feedback Actions
**Tiga tombol di panel bawah:**

1. **Benar** — kirim feedback positif, produk masuk tray "Sudah Dicek", modal lanjut ke produk berikutnya
2. **Salah** — kirim feedback negatif, produk masuk tray, modal lanjut ke produk berikutnya
3. **Buka Produk** — membuka halaman Tokopedia di tab baru tanpa menutup modal

Tutup modal: tombol ×, klik backdrop, atau tombol Escape. Scroll halaman utama dikunci saat modal terbuka (`html.modal-open`, `body.modal-open`).

### Navigasi Queue
- Setiap feedback submit → sistem pindah ke produk berikutnya di queue
- Queue = hasil scrape (atau filtered berdasarkan kategori aktif)
- Jika semua produk sudah direview → modal auto-close

### Responsive Behavior
- **Desktop (≥1100px)**: Grid 2 kolom (image left, content right)
- **Tablet (701-1100px)**: Stacked 1 kolom, image di atas
- **Mobile (≤700px)**: Full-width, image max 240px, all scrollable

---

## 🔧 Troubleshooting

### ❌ Error: Port 3000 Sudah Dipakai
**Gejala**: `[Errno 10048] error while attempting to bind on address ('127.0.0.1', 3000)`

**Solusi:**
1. **Cari process yang pakai port 3000**:
   ```bash
   netstat -ano | findstr :3000
   ```
2. **Kill process (Windows)**:
   ```bash
   taskkill /PID <PID> /F
   ```
   atau ubah PORT:
   ```bash
   $env:PORT=3005; python app.py
   ```

### ⏱️ Error: Ollama Timeout (75s)
**Gejala**: "AI response timeout after 75 seconds"

**Penyebab**: Model running lambat atau hardware underpowered

**Solusi**:
1. Pastikan Ollama running (`ollama serve`)
2. Increase timeout:
   ```env
   AI_CHAT_TIMEOUT_SECONDS=120
   ```
3. Reduce batch size:
   ```env
   AI_BATCH_SIZE=1
   ```
4. Restart app

### 🖼️ Error: Gambar Produk Tidak Tampil
**Gejala**: Image placeholder "TIDAK ADA GAMBAR" terus muncul

**Penyebab**: 
- Tokopedia blocked image hotlink, atau
- Image URL expired

**Solusi**:
- System auto-fallback ke placeholder (normal behavior)
- Gambar yang rusak bisa di-fix di Ollama audit phase

### 💾 Error: "Cache Corrupted" atau Feedback Tidak Tersimpan
**Gejala**: Aplikasi restart, feedback hilang

**Solusi**:
1. Clear cache:
   ```bash
   rm -rf data/ai_memory/*  # Linux/macOS
   rmdir /S data\ai_memory  # Windows
   ```
2. Restart app

### UI Belum Berubah karena Cache Browser
**Gejala**: Perubahan `web/app.js` atau `web/style.css` tidak terlihat setelah refresh biasa.

**Solusi**:
1. Lakukan hard refresh: `Ctrl+Shift+R` (Windows) atau `Cmd+Shift+R` (macOS).
2. Pastikan query string cache-bust di `index.html` terbaru (`style.css?v=...`, `app.js?v=...`).
3. Tutup tab lama, buka ulang `http://127.0.0.1:3000`.

### JavaScript Function is Not Defined
**Gejala**: Overlay error seperti `getFastCategoryMotionProfile is not defined` atau `getOrbMorphProfile is not defined`.

**Penyebab**: Cache browser masih memuat `app.js` lama yang memanggil helper motion profile yang sudah diganti.

**Solusi**:
1. Hard refresh browser (lihat bagian cache di atas).
2. Pastikan hanya file di folder `web/` yang disajikan (`src/server/main.py` mount `/static` ke `web/`).
3. Cari di `web/app.js` — pemanggilan harus memakai `getCategoryMotionProfile()`.

### Modal atau Detail Produk Menampilkan Scrollbar Horizontal
**Gejala**: Modal detail produk memiliki scrollbar horizontal atau konten terpotong di sisi kanan.

**Penyebab**: Lebar modal atau judul produk melebihi viewport; aturan CSS lama bertabrakan.

**Solusi**:
1. Hard refresh agar `web/style.css` terbaru dimuat.
2. Pastikan modal memakai struktur `.product-modal-backdrop` + `.product-detail-modal` (bukan `<dialog>` lama).
3. Semua anak modal harus memiliki `min-width: 0` dan lebar `min(..., calc(100vw - ...))`.

### 🌐 Error: Browser CORS atau JavaScript Error
**Gejala**: Console penuh red error, modal tidak buka

**Solusi**:
1. Buka DevTools (F12)
2. Periksa Console tab untuk error detail
3. Screenshot error dan report
4. Cek file `web/app.js` valid:
   ```bash
   node -c web/app.js
   ```

### 📊 Error: "No products found" padahal scrape selesai
**Gejala**: Progress selesai tapi produk kosong

**Penyebab**: 
- Query tidak ada hasil, atau
- Semua produk di-filter out oleh AI (0 confidence)

**Solusi**:
1. Coba query umum: "laptop" bukan "laptop gaming amd ryzen ultra 16 inti"
2. Disable AI check:
   ```env
   AI_AUDIT_MAX_PRODUCTS=0  # Disable AI, gunakan rules saja
   ```
3. Lower AI confidence threshold (TBD di future release)

---

## 📝 Catatan Pengembangan

### Tech Stack
- **Backend**: FastAPI + Uvicorn (Python 3.8+)
- **Scraper**: Puppeteer (Node.js) + Selenium (Python)
- **AI**: Ollama (gemma3:4b, llama3.2:3b, phi4-mini)
- **Frontend**: Vanilla JS + Anime.js + CSS3
- **Testing**: Pytest + Playwright

### File Penting
| File | Peran | Baris |
|------|-------|-------|
| `app.py` | Entry app, start uvicorn | ~50 |
| `src/server/main.py` | FastAPI routes | ~200 |
| `src/ai/orchestrator.py` | AI eval logic | ~300 |
| `src/scraper/puppeteer.js` | Tokopedia scrape | ~500 |
| `web/app.js` | Frontend controller | ~4000 |
| `web/style.css` | Responsive styling | ~4000 |

### Development Mode
```bash
# Watch + reload (manual)
python app.py  # One terminal
# Edit web/app.js atau web/style.css → browser F5 refresh

# Debugging (add breakpoint di app.js)
# Browser DevTools (F12) → Sources → set breakpoint
```

### Testing
```bash
pytest tests/                          # Run all tests
pytest tests/test_integration.py -v    # Specific test file
pytest tests/ -k "test_budget"         # Filter by name
```

### Build/Deploy
- **Local**: `python app.py` → http://127.0.0.1:3000
- **Production**: TBD (containerize dengan Docker)

### Future Roadmap
- [ ] Export hasil ke CSV/JSON
- [ ] Integration Telegram Bot untuk progress notify
- [ ] Multi-marketplace (Shopee, Lazada, dll)
- [ ] Advanced filtering (category, rating range, seller tier)
- [ ] API auth & user profiles
- [ ] Dark mode toggle (current: always dark)

---

## ⚠️ Batasan Sistem

### Hardware
- **Minimum**: Laptop i5 + 8GB RAM + 2GB disk (dengan Ollama lokal sangat demanding)
- **Recommended**: i7 + 16GB RAM + SSD 256GB + GPU dedicated

### AI Lokal
- **Model Size**: gemma3:4b = ~2.5GB RAM, llama3.2:3b = ~2GB, phi4-mini = ~1.5GB → Total ~6GB active
- **Batch Size**: Max 3 produk per batch untuk menjaga responsive (configurable ke 5-10 jika GPU available)
- **Timeout**: 75 detik per batch (dapat di-tuning via env)
- **Fallback**: Jika Ollama down, sistem fallback ke rules berbasis keyword (no AI)

### Scraping
- **Browser**: Puppeteer headless, single instance (no parallel crawling yet)
- **Timeout Page**: 30 detik per halaman (configurable)
- **Retry Logic**: Up to 3 retries per page, then skip
- **Rate Limit**: Respect Tokopedia rate-limiting (auto-delay 1-3s per request)

### Frontend
- **Tested Browsers**: Chrome 120+, Edge 120+, Firefox 121+
- **Mobile**: iOS Safari 15+, Chrome Android 120+
- **JS**: Vanilla ES6 (no build step, direct browser execution)
- **Animasi**: Anime.js v3+ (SVG drawable support, fallback to CSS)

### Data Privacy
- **Local Only**: Semua data disimpan lokal (~/RB-C1/data/)
- **No Cloud**: Tidak ada sync ke server cloud
- **Offline**: Aplikasi fully functional offline (kecuali Tokopedia scrape)

### Kinerja
- **Search Result**: 50 produk = ~2-5 menit scrape + 1-3 menit AI eval (tergantung hardware)
- **UI Responsivity**: Semua animasi 60fps (Anime.js optimized)
- **Memory**: Peak ~500MB dengan 50 produk + Ollama running

### Limitation Dikenal
1. **Single Browser Instance**: Tidak support parallel scraping yet
2. **Ollama RAM**: Aggressive untuk laptop standar (harus manage browser/app lain)
3. **Dynamic Content**: Jika Tokopedia add lazy-loading baru, scraper mungkin perlu update
4. **No Export Yet**: Hasil hanya bisa lihat di UI (export feature TBD)
5. **No Auth**: Aplikasi public (no login), suitable untuk lokal use only

---

## 📞 Support & Kontribusi

### Report Bug
Buat issue di repository dengan:
- Deskripsi error
- Screenshot / terminal output
- Hardware spec (CPU, RAM, GPU)
- Ollama status (`ollama list`)

### Kontribusi
1. Fork repo
2. Create feature branch (`git checkout -b feature/xyz`)
3. Commit changes
4. Push & open PR

---

**Terima kasih telah menggunakan PasarIntai AI! 🚀**
  ```bash
  PORT=3005 python app.py
  ```

### Ollama Timeout
1. Pastikan servis Ollama sudah berjalan aktif (`ollama serve` atau aplikasi desktop Ollama menyala).
2. Gunakan perintah `ollama run <model>` di terminal untuk memastikan model telah terunduh sempurna.
3. Tetapkan `AI_AUDIT_MAX_PRODUCTS=3` guna menghindari overload antrean pemrosesan di CPU lokal.

### Gambar Produk Tidak Muncul
Beberapa gambar marketplace dilindungi oleh proteksi hotlink. Aplikasi menyediakan proxy gambar bawaan secara otomatis. Jika ada beberapa gambar yang masih gagal tampil, periksa konektivitas jaringan Anda.

### UI Tidak Berubah Karena Cache Browser
FastAPI telah dikonfigurasi untuk mengirim header kontrol no-cache. Namun apabila perubahan layout/style tidak langsung terlihat, bersihkan cache browser Anda secara paksa (*Hard Refresh*) dengan tombol shortcut `Ctrl + F5` (Windows) atau `Cmd + Shift + R` (macOS).

### Error JavaScript "Function Not Defined"
Pastikan library Anime.js (`vendor/anime.min.js`) dan skrip `app.js` dimuat dengan benar tanpa ada ekstensi browser (seperti adblocker keras) yang memblokir request file lokal. Semua fungsi kini dideklarasikan dengan teknik hoisting (function declaration) untuk mencegah kegagalan inisialisasi urutan pemuatan script.

## Catatan Pengembangan

- **Penyimpanan Hasil Sementara**: Data hasil pencarian disimpan sementara di memori server (in-memory) dan akan direset setiap kali server dimulai ulang.
- **Model AI Lokal**: Performa kecepatan audit semantik dan perbaikan JSON sepenuhnya bergantung pada kekuatan kapasitas RAM dan kemampuan prosesor laptop Anda.
- **Feedback & Pembelajaran**: Feedback kurasi Benar/Salah yang Anda berikan disimpan dalam database lokal pada folder `data/` guna membantu sistem mempelajari relevansi produk dari waktu ke waktu. Jangan menghapus folder database tersebut jika ingin mempertahankan memori pembelajaran sistem.
