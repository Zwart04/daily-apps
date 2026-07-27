# Daily Apps

Kumpulan aplikasi web dan tool command-line yang dibangun satu per hari oleh Hermes Agent untuk Muammar Fikri.

Live: https://daily-apps.pages.dev

## Aplikasi Web (folder apps/)

| Aplikasi | Deskripsi |
|---|---|
| warkah | Surat digital time-locked, data di URL hash, tanpa server |
| retouch | Editor visual untuk HTML hasil AI (paste, edit, export) |
| formie | Form builder drag-and-drop, ekspor HTML bersih |
| thema | Generator tema warna dari gambar (CSS vars, Tailwind, shadcn/ui) |
| crispdata | Pembersih dan konverter data (Markdown, JSON, CSV, HTML) |
| devtoolkit-pro | 12 utilitas developer dalam satu halaman |
| kata-kilat | Game tebak kata Bahasa Indonesia dari definisi |
| penghitung-kurs | Konversi 22 mata uang dengan kurs live |

## Tool Command-Line (folder tools/)

| Tool | Deskripsi |
|---|---|
| ctx | Ekstrak codebase jadi satu file konteks untuk AI assistant |
| certwatch | Cek masa berlaku sertifikat SSL/TLS massal |
| gittree | Operasi git massal lintas repo |
| envdoctor | Scan dan validasi environment variable |
| catatan-cepat | Catatan cepat dari terminal |
| pembersih-duplikat | Cari dan hapus file duplikat |

Tool CLI dipakai dengan clone repo ini lalu ikuti README di folder masing-masing.

## Struktur

- `index.html` — landing page
- `apps/<nama>/` — aplikasi web, masing-masing berdiri sendiri
- `tools/<nama>/` — tool CLI Python

Semua konten digabung dari repo-repo harian terdahulu (Juni-Juli 2026) menjadi satu monorepo.
