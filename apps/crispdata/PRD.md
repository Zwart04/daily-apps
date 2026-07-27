# CrispData v1 — Mini PRD

## Masalah
Ketika orang copy-paste data dari AI tools (ChatGPT, Claude, Gemini), hasilnya sering campur aduk format dan berantakan: tabel Markdown dengan pipa tidak rapi, JSON dengan trailing comma atau indentasi campuran, CSV dengan quoting tidak konsisten, atau bahkan data penuh karakter tak terlihat (zero-width spaces, unicode artifacts).

Untuk membersihkannya, orang harus:
1. Buka tool converter A buat format X
2. Buka tool converter B buat format Y
3. Copy-paste manual ke Excel/Google Sheets
4. Manual hapus karakter aneh

Belum ada tool gratis yang menggabungkan auto-detect + clean + convert dalam satu step.

## Target Pengguna
Siapa pun yang sering copas data dari AI tools, database, Slack, email, spreadsheet — data analyst, product manager, developer, peneliti, mahasiswa.

## Kenapa Beda dari yang Sudah Ada
- **tableconvert.com** — hanya handle tabel, harus pilih format manual
- **cleanpaste.org** — cuma bersihin invisible chars, gak bisa konversi format
- **OpenRefine** — powerful tapi harus install, overkill buat quick clean-up
- **JSON ↔ CSV converters** — satu arah, gak auto-detect, gak clean
- **CrispData** — auto-detect format input + clean invisible chars + convert ke SEMUA format populer + zero-install + 100% browser (privacy)

## Fitur Inti MVP
1. **Smart Paste** — area paste dengan auto-detect format (Markdown table, JSON array, CSV, TSV, HTML table, pipe-delimited text)
2. **Data Viewer** — preview data sebagai tabel yang rapi
3. **Format Conversion** — convert antara Markdown table, JSON, CSV, HTML table (dengan copy button)
4. **Smart Clean** — auto-remove invisible chars, normalize quotes, fix trailing commas di JSON, trim whitespace
5. **Stats** — row count, column count, format terdeteksi
6. **Dark theme** — default dark mode (konsisten dengan Retouch)
7. **Copy one-click** — copy hasil cleaned/converted

## Non-Fitur (Out of Scope v1)
- Excel file upload (.xlsx) — cukup paste data mentah
- CSV file export — cukup copy to clipboard
- Data editing (edit cell) — cukup clean + convert
- API / server — 100% client-side

## Tech Stack
- Vanilla JS (satu file HTML, nol dependency)
- Tailwind CSS v4 CDN (via @tailwindcss/browser)
- Deploy ke GitHub Pages
