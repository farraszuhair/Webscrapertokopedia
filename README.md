# PasarIntai AI

PasarIntai AI adalah aplikasi lokal untuk scraping produk marketplace, menyaring hasil berdasarkan budget, membantu evaluasi relevansi dengan AI lokal, dan menyimpan feedback pengguna agar kurasi produk semakin akurat.

## Fitur Utama

- Scraping produk Tokopedia dengan Puppeteer dan fallback Selenium.
- Filter budget dengan toleransi persentase.
- Evaluasi relevansi produk memakai AI lokal melalui Ollama, dengan fallback rules saat model tidak tersedia.
- Rekomendasi cepat berdasarkan empat kategori: Semua Barang, Terbaik, Termurah, dan Most Trusted.
- Feedback produk melalui tombol Benar, Salah, dan Buka Produk.
- Produk yang sudah diberi feedback otomatis pindah ke kotak Sudah Dicek.
- UI midnight blue yang bersih, responsif, dan mudah dipindai.

## Tampilan UI

Header menampilkan logo PI, judul PasarIntai AI, subtitle scraping produk, dan status aplikasi di kanan atas.

Status aplikasi memakai badge/pill normal:

- Siap
- Berjalan
- Selesai
- Error

Badge status dibuat sebagai pill teks biasa yang stabil dan mudah dibaca.

## Rekomendasi Cepat

Panel Rekomendasi Cepat memakai card besar rounded dengan tombol kategori berbentuk pill modern.

Kategori yang tersedia:

- Semua Barang: menampilkan semua produk hasil scrape yang belum dicek.
- Terbaik: mengutamakan produk dengan skor/kepercayaan AI tertinggi.
- Termurah: mengurutkan produk dari harga terendah.
- Most Trusted: mengutamakan kombinasi rating dan jumlah terjual.

Saat kategori diklik, UI hanya mengganti active state tombol lalu merender ulang produk dengan transisi ringan fade/stagger. Tidak ada overlay kategori, tab duplikat, ikon membesar, atau animasi perpindahan kamera.

## Product Card

Setiap product card menampilkan:

- Gambar produk atau placeholder jika gambar tidak tersedia.
- Nama produk.
- Harga dengan warna hijau.
- Rating dan jumlah terjual.

Card bisa diklik untuk membuka detail produk.

## Modal Detail Produk

Modal detail produk adaptif untuk desktop, tablet, dan mobile. Layout menjaga konten tetap berada dalam viewport dan tidak membuat horizontal scrollbar.

Aksi modal:

- Benar: menyimpan feedback positif dan memindahkan produk ke Sudah Dicek.
- Salah: menyimpan feedback negatif dan memindahkan produk ke Sudah Dicek.
- Buka Produk: membuka halaman produk marketplace.

Setelah feedback dikirim, modal lanjut ke produk berikutnya jika masih ada antrean review.

## Cara Menjalankan

Prasyarat:

- Python 3.8+
- Node.js 18+
- Ollama opsional untuk evaluasi AI lokal

Instal dependensi:

```bash
pip install -r requirements.txt
npm install
```

Jalankan aplikasi:

```bash
python app.py
```

Buka aplikasi di browser:

```text
http://127.0.0.1:3000
```

## Konfigurasi AI Lokal

Model yang direkomendasikan:

```bash
ollama pull gemma3:4b
ollama pull llama3.2:3b
ollama pull phi4-mini
ollama pull nomic-embed-text
```

Contoh konfigurasi `.env`:

```env
AI_MODEL=gemma3:4b
AI_AUDIT_MAX_PRODUCTS=3
AI_BATCH_CLASSIFY=true
AI_BATCH_SIZE=3
AI_CHAT_TIMEOUT_SECONDS=75
PUPPETEER_HEADLESS=true
PUPPETEER_TIMEOUT=30000
PORT=3000
LOG_LEVEL=INFO
```

## Struktur Project

```text
RB-C1/
├── app.py
├── requirements.txt
├── package.json
├── README.md
├── web/
│   ├── index.html
│   ├── app.js
│   ├── style.css
│   └── vendor/
├── src/
│   ├── ai/
│   ├── scraper/
│   ├── server/
│   └── utils/
├── tests/
└── data/
```

## Testing

Jalankan test Python:

```bash
pytest
```

Cek syntax JavaScript:

```bash
node -c web/app.js
```

## Catatan UI

- Tema utama tetap midnight blue.
- Status kanan atas adalah badge normal.
- Pergantian kategori memakai fade/stagger ringan.
- Modal detail produk dibuat tanpa horizontal scrollbar.
- Kode animasi kategori lama yang tidak dipakai sudah dinonaktifkan atau dihapus dari UI utama.
