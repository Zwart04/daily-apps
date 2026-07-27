# Pembersih File Duplikat

**Temukan dan bersihkan file duplikat di komputer Anda dengan mudah.**

Pernah punya folder Downloads yang penuh file dobel? Atau folder foto dengan 
ratusan duplikat yang menghabiskan ruang penyimpanan? Aplikasi ini membantu 
Anda menemukan file-file duplikat itu dan membersihkannya.

## Fitur

- **Cari file duplikat** — Temukan file yang isinya sama persis, walaupun namanya berbeda
- **Cepat & efisien** — Proses 2 tahap (hash awal, hash penuh) untuk hasil cepat
- **Aman** — Mode kering (dry-run) untuk lihat dulu sebelum hapus
- **Output jelas** — Lihat grup duplikat, ukuran, dan total ruang yang terbuang
- **Tanpa dependency** — Hanya pakai Python standar, tidak perlu install library tambahan

## Cara Pakai

### Persyaratan
- Python 3.10 atau lebih baru
- Tidak perlu install library tambahan

### Langkah 1: Download atau clone

```bash
git clone https://github.com/.../pembersih-duplikat.git
cd pembersih-duplikat
```

### Langkah 2: Cari duplikat

Periksa folder Downloads:

```bash
python3 -m src ~/Downloads
```

Atau folder foto:

```bash
python3 -m src ~/Gambar
```

### Langkah 3: Lihat dulu (mode kering)

Lihat file apa saja yang akan dihapus (tanpa benar-benar menghapus):

```bash
python3 -m src ~/Downloads --kering
```

### Langkah 4: Hapus duplikat

Setelah yakin, hapus file duplikat:

```bash
python3 -m src ~/Downloads --hapus
```

### Contoh lainnya

```bash
# Output JSON (untuk diproses program lain)
python3 -m src ~/Downloads --json

# Abaikan file kecil (< 5 MB)
python3 -m src ~/Downloads --min-size 5242880

# Self-test
python3 -m src --test
```

## Konfigurasi

| Variable | Deskripsi | Default |
|----------|-----------|---------|
| `PDF_EXCLUDE_DIRS` | Folder yang dilewati (pisah dengan koma) | `.git,__pycache__,node_modules,...` |
| `PDF_MIN_SIZE` | Ukuran minimal file (byte) | `1024` (1 KB) |
| `PDF_CHUNK_SIZE` | Ukuran baca per hash (byte) | `65536` (64 KB) |

Contoh:
```bash
export PDF_EXCLUDE_DIRS=".git,node_modules,.cache,temp"
python3 -m src ~/Downloads
```

## Cara Kerja

1. **Scan folder** — Kumpulkan semua file (kecuali folder sistem)
2. **Kelompokkan ukuran** — File dengan ukuran sama masuk grup yang sama
3. **Hash awal** — Hitung hash dari 64 KB pertama file (cepat)
4. **Hash penuh** — Untuk file dengan hash awal sama, hitung hash seluruh file
5. **Output** — Tampilkan grup duplikat

Dua tahap hash membuat proses jauh lebih cepat: file berbeda biasanya sudah ketahuan dari 64 KB pertama.

## Arsitektur

```
src/
  __init__.py   — Public API
  __main__.py   — Entry point python3 -m src
  cli.py        — CLI parser + orchestration + self-test
  config.py     — Config loader (env vars)
  core.py       — Core logic (scan, hash, group)
  formatter.py  — Output formatter (text, JSON)
  types.py      — Type definitions
```

## Filosofi Desain

1. **Zero dependency** — Hanya stdlib Python, langsung jalan tanpa ribet install
2. **Aman dulu** — Mode kering (dry-run) sebelum hapus, biar tidak nyesel
3. **Cepat dengan 2-tahap hash** — 64 KB pertama cukup untuk 99% file berbeda
4. **Satu masalah, satu alat** — Hanya cari dan bersihkan duplikat, tidak jadi Swiss Army Knife

## Lisensi

MIT
