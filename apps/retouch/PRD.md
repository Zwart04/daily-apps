# Retouch v4 — Mini PRD

## Masalah
Retouch v3 sudah bisa edit teks, warna, font, dan urutan elemen (via tombol up/down). Tapi belum ada drag-and-drop visual — fitur yang paling membedakan editor biasa dari Elementor/Divi. Pengguna masih harus klik tombol berkali-kali untuk mindahin elemen.

## Target Pengguna
Orang non-teknis yang generate website pakai AI (ChatGPT, Claude, v0, Bolt) tapi ga bisa nulis/mengerti HTML. Mereka butuh tool gratis, zero-install, yang bisa edit hasil generate AI secara visual kayak Elementor.

## Fitur Inti v4
1. **Drag-and-drop posisi elemen** — klik & seret elemen (via handle) ke posisi baru di preview. Visual indicator garis putus-putus muncul di antara elemen pas drag.
2. **Image URL editor** — klik gambar yang dipilih, muncul input buat ganti src URL.
3. **Margin controls** — preset margin (none, small, medium, large) via toolbar.
4. **Width presets** — full-width, contained, auto, half-width.
5. **Grid background toggle** — toggle grid overlay biar alignment keliatan.
6. **Smart preview** — tombol toggle buat liat hasil di ukuran Desktop / Tablet / Mobile.

## Tech Stack
- Vanilla JS (sama seperti v3, zero dependency)
- Tailwind CSS v4 CDN (via @tailwindcss/browser)
- Satu file index.html, deploy ke GitHub Pages

## Kenapa Beda dari yang Sudah Ada
- Gratis total, no signup, no server
- Fokus spesifik: edit hasil AI-generated HTML
- Zero-install, buka browser langsung pakai
- GrapesJS/Webstudio terlalu kompleks untuk orang non-teknis
