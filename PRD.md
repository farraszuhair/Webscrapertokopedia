# PRD — Clean Human-Like Web Scraping Dashboard

## 1. Nama Produk
MarketSpy AI — Clean Human-Like Scraping Dashboard

## 2. Tujuan Produk
Membuat aplikasi web scraping yang:
- Memiliki tampilan web yang clean, modern, user-friendly, dan mudah dipahami.
- Menampilkan proses scraping secara real-time dengan progress, elapsed time, ETA, dan log singkat.
- Menghasilkan data produk yang rapi, relevan, dan sesuai jumlah target user.
- Memiliki alur scraping yang terlihat natural dan tidak agresif.
- Memiliki struktur kode yang bersih, modular, mudah di-debug, dan siap dikembangkan.

## 3. Masalah Saat Ini
Project scraping saat ini masih memiliki beberapa masalah:
- UI terlalu padat, kurang rapi, dan kurang ramah untuk user awam.
- Progress scraping sering tidak real-time atau stuck.
- Jumlah produk yang tampil sering tidak sesuai target.
- Filtering AI kadang terlalu ketat sehingga produk valid ikut dibuang.
- Kode scraping, filtering, progress, dan UI masih tercampur.
- Error handling belum cukup jelas untuk user dan developer.
- Belum ada standar struktur project yang clean.

## 4. Target User
User utama adalah mahasiswa/developer yang ingin:
- Mencari produk dari marketplace.
- Membandingkan harga, rating, toko, dan jumlah terjual.
- Mendapat rekomendasi produk terbaik secara cepat.
- Melihat progress scraping dengan jelas.
- Memberikan feedback ke AI ketika hasil salah.

## 5. Scope Fitur Utama

### 5.1 Landing Page / Search Page
UI harus memiliki:
- Tampilan clean, modern, dan responsive.
- Form input query produk.
- Input jumlah target produk.
- Optional budget toggle.
- Input budget yang menerima format Indonesia, contoh: `12.000.000`.
- Input toleransi budget dalam persen.
- Tombol `Mulai Scraping`.
- Copywriting yang natural, bukan teknis berlebihan.

### 5.2 Progress Scraping
Saat scraping berjalan, tampilkan:
- Progress percentage.
- Status text.
- Elapsed time real-time.
- ETA real-time.
- Jumlah produk ditemukan, contoh: `32 / 50 produk`.
- Log singkat yang mudah dibaca.
- State visual:
  - Preparing browser
  - Opening marketplace
  - Collecting products
  - Deduplicating
  - Filtering budget
  - AI crosscheck
  - Finalizing result

### 5.3 Result Page / Result Section
Hasil produk harus ditampilkan dengan:
- Grid card yang rapi.
- Gambar produk.
- Nama produk.
- Harga.
- Rating.
- Jumlah terjual.
- Nama toko.
- Link produk.
- Badge confidence / AI score jika ada.
- Tombol feedback:
  - `Benar`
  - `Salah`

### 5.4 Quick Filter Box
Di atas hasil scraping, wajib ada box filter:
- `Most Trusted`
- `Termurah`
- `Terbaik`

Behavior:
- `Most Trusted`: urutkan berdasarkan rating, sold count, dan reputasi toko jika tersedia.
- `Termurah`: urutkan berdasarkan harga termurah.
- `Terbaik`: ranking gabungan dari relevansi query, rating, harga, dan sold count.

### 5.5 Feedback AI Learning
Saat user klik `Salah`, tampilkan modal:
- Pilihan alasan multi-select:
  - Produk tidak relevan
  - Harga tidak sesuai
  - Bukan produk utama
  - Duplikat
  - Rating/toko mencurigakan
  - Data tidak lengkap
  - Lainnya
- Input catatan tambahan opsional.
- Simpan feedback ke local storage atau file JSON/backend endpoint.
- Feedback tidak boleh membuat AI langsung menganggap semua produk mirip sebagai salah secara permanen.
- Learning harus berbasis konteks query.
  Contoh:
  - Kalau query `RTX 5060` lalu user salahkan produk `RTX 4060`, sistem tidak boleh otomatis menolak `RTX 4060` ketika user memang mencari `RTX 4060`.

### 5.6 Human-Like Scraping Behavior
Scraping harus berjalan secara bertanggung jawab:
- Gunakan delay kecil dan wajar antar aksi.
- Scroll bertahap, bukan spam.
- Tunggu elemen penting muncul sebelum ekstraksi.
- Gunakan retry terbatas dengan backoff.
- Jangan melakukan bypass captcha.
- Jangan melakukan bypass login, paywall, atau proteksi ilegal.
- Jangan menggunakan teknik stealth agresif, proxy abuse, atau fingerprint spoofing ekstrem.
- Jika muncul captcha/blocking, hentikan scraping dan tampilkan pesan jelas ke user.

### 5.7 Data Quality
Setiap produk minimal memiliki:
- `id`
- `title`
- `price`
- `priceNumber`
- `image`
- `storeName`
- `rating`
- `soldCount`
- `url`
- `source`
- `confidenceScore`
- `relevanceReason`

Validasi:
- Harga harus bisa diparse dari format Indonesia.
- Produk duplikat harus dibuang berdasarkan URL/title similarity.
- Produk tanpa harga valid jangan langsung dibuang jika masih bisa diperbaiki dari teks lain.
- Target display harus sebisa mungkin sesuai request user.
- Jika target 50, sistem harus overfetch lebih banyak, contoh 70–100 kandidat, lalu filter sampai 50.

## 6. Non-Functional Requirements

### 6.1 Performance
- UI tidak boleh freeze saat scraping.
- Progress harus update minimal setiap 500ms–1s.
- Backend harus mengirim progress secara incremental.
- Scraping harus timeout dengan pesan error yang jelas.

### 6.2 Maintainability
Kode harus dipisah menjadi:
- Scraper engine
- Parser
- Deduplicator
- Budget filter
- AI filter
- Feedback learning
- Progress manager
- API routes
- UI components

### 6.3 Observability
Wajib ada logging:
- Search started
- Browser opened
- Marketplace loaded
- Products collected
- Dedup completed
- Budget filter completed
- AI filter completed
- Final result generated
- Error with stack trace for developer

### 6.4 Error Handling
User-facing error harus jelas:
- Marketplace gagal dibuka
- Produk tidak ditemukan
- Terblokir captcha
- Model AI tidak tersedia
- Budget terlalu ketat
- Scraper timeout
- Server error

Developer error tetap disimpan di log/debug file.

## 7. Suggested Project Structure

```txt
project-root/
├─ backend/
│  ├─ main.py
│  ├─ api/
│  │  ├─ routes_search.py
│  │  ├─ routes_progress.py
│  │  └─ routes_feedback.py
│  ├─ core/
│  │  ├─ config.py
│  │  ├─ logger.py
│  │  └─ progress.py
│  ├─ scraper/
│  │  ├─ engine.py
│  │  ├─ parser.py
│  │  ├─ human_behavior.py
│  │  └─ tokopedia.py
│  ├─ services/
│  │  ├─ dedupe_service.py
│  │  ├─ budget_service.py
│  │  ├─ ai_filter_service.py
│  │  └─ feedback_service.py
│  └─ storage/
│     ├─ feedback.json
│     └─ debug/
│
├─ frontend/
│  ├─ index.html
│  ├─ src/
│  │  ├─ main.js
│  │  ├─ api.js
│  │  ├─ state.js
│  │  ├─ utils/
│  │  │  ├─ formatPrice.js
│  │  │  └─ time.js
│  │  └─ components/
│  │     ├─ SearchForm.js
│  │     ├─ ProgressPanel.js
│  │     ├─ FilterTabs.js
│  │     ├─ ProductGrid.js
│  │     ├─ ProductCard.js
│  │     └─ FeedbackModal.js
│  └─ styles/
│     └─ app.css
│
├─ docs/
│  └─ PRD.md
├─ .env.example
└─ README.md

8. Acceptance Criteria

Project dianggap selesai jika:

UI terlihat clean, rapi, responsive, dan mudah digunakan.
User bisa input query, target produk, budget opsional, dan toleransi.
Progress, elapsed, ETA, status, dan log berjalan real-time.
Hasil produk tampil dalam card grid yang rapi.
Quick filter Most Trusted, Termurah, dan Terbaik berjalan.
Tombol Benar dan Salah tersedia di setiap produk.
Modal feedback muncul hanya saat klik Salah.
Feedback tersimpan dan dipakai secara kontekstual.
Scraper tidak agresif dan memiliki retry/backoff wajar.
Jika terjadi captcha/blocking, sistem berhenti dengan pesan jelas.
Kode dipisah modular dan tidak ada file sampah yang tidak dipakai.
Tidak ada dummy/stub palsu di fitur utama.