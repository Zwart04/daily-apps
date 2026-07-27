# Catatan Cepat

**Catat apapun dari terminal dengan cepat. Gantungan kunci catatan untuk programmer dan siapapun yang kerja di terminal.**

Catatan Cepat adalah alat baris perintah (CLI) untuk mencatat ide, tugas, catatan harian, atau apapun langsung dari terminal. Data disimpan di folder `~/.catatan-cepat/` sebagai file JSON — aman, privat, dan tidak perlu internet.

## Features

- **Catat cepat** — `python3 -m src catat "Ide aplikasi"` langsung tersimpan
- **Cari catatan** — cari berdasarkan kata kunci atau tag
- **Tag dan filter** — kelompokkan catatan dengan tag, filter nanti
- **Export** — export ke JSON atau Markdown
- **Statistik** — lihat jumlah catatan dan tag terpopuler
- **Tanpa dependency** — hanya pakai Python standar, langsung jalan
- **100% offline** — data disimpan di komputer anda sendiri

## Quick Start

### Langsung pakai

```bash
# Buat catatan baru
python3 -m src catat "Belanja mingguan: telur, susu, roti"

# Buat catatan dengan tag
python3 -m src catat "Ide aplikasi catatan" --tag ide

# Lihat semua catatan
python3 -m src lihat

# Cari catatan
python3 -m src cari "belanja"

# Lihat detail catatan
python3 -m src detail <ID_CATATAN>

# Lihat statistik
python3 -m src stats
```

### Cara install (opsional)

```bash
# Install sebagai perintah sistem
pip install -e .

# Setelah install, bisa langsung:
catatan-cepat catat "Halo dunia"
```

## Usage

### Perintah lengkap

| Perintah | Fungsi |
|----------|--------|
| `catat <judul>` | Buat catatan baru |
| `catat <judul> --isi <isi> --tag <tag>` | Buat catatan dengan isi dan tag |
| `lihat` / `l` | Lihat daftar catatan |
| `cari <kata>` / `s <kata>` | Cari catatan |
| `tag <nama>` | Lihat catatan dengan tag tertentu |
| `detail <id>` / `d <id>` | Lihat detail catatan |
| `hapus <id>` / `rm <id>` | Hapus catatan |
| `export [file]` | Export ke JSON atau Markdown |
| `stats` | Lihat statistik |
| `test` | Jalankan tes mandiri |

### Contoh

```bash
# Catat ide dengan isi panjang
python3 -m src catat "Rencana liburan" \
  --isi "Bali 3 hari, Jakarta 2 hari. Budget: 5 juta." \
  --tag liburan

# Lihat catatan dengan tag 'ide'
python3 -m src tag ide

# Export semua catatan
python3 -m src export catatan_saya.json

# Export catatan dengan tag 'kerja' ke Markdown
python3 -m src export catatan_kerja.md --format markdown --tag kerja

# Hapus catatan
python3 -m src hapus 20260705123456
```

## Configuration

Catatan disimpan di `~/.catatan-cepat/catatan.json`. Tidak ada konfigurasi lain yang diperlukan.

| Variable | Default | Deskripsi |
|----------|---------|-----------|
| `CATATAN_DIR` | `~/.catatan-cepat` | Folder penyimpanan catatan |

Ubah folder penyimpanan:

```bash
CATATAN_DIR=~/notes python3 -m src catat "Catatan ini disimpan di folder notes"
```

## Data Privacy

Semua catatan disimpan **lokal** di komputer anda. Tidak ada data yang dikirim ke internet. File JSON bisa dibaca dan diedit manual jika perlu.

## Architecture

```
src/
  __init__.py   — Export fungsi utama
  __main__.py   — Entry point python3 -m src
  cli.py        — Antar muka baris perintah + tes mandiri
  store.py      — Penyimpanan JSON ke folder ~/.catatan-cepat/
  core.py       — Logika bisnis (NoteManager)
  types.py      — Tipe data (Note, FilterOptions)
  formatter.py  — Format output terminal
```

## Design Philosophy

1. **Cepat dan ringan** — tidak perlu database, server, atau internet. Buka terminal, catat, selesai.
2. **Privasi dulu** — data 100% di komputer anda. Tidak ada cloud, tidak ada tracking.
3. **Satu perintah, selesai** — `python3 -m src catat "isi"` adalah satu-satunya yang perlu diingat.
4. **Zero dependency** — tidak perlu install Python package tambahan. Bawaan Python sudah cukup.

## License

MIT
