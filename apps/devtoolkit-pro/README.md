# DevToolKit Pro 🛠️

DevToolKit Pro adalah aplikasi web single-file self-contained (HTML, CSS, JS terintegrasi) yang menyediakan 12 alat utilitas pengembang (developer utilities) super lengkap dan siap pakai.

## 📥 Link Download Langsung

Anda bisa mengunduh produk jadi siap pakai melalui link berikut:

- **[Download Singe-File HTML (Langsung Jalankan)](https://github.com/Zwart04/devtoolkit-pro/releases/download/v1.0.0/index.html)**
- **[Download ZIP Web App (Extract & Buka)](https://github.com/Zwart04/devtoolkit-pro/releases/download/v1.0.0/devtoolkit-pro.zip)**

---

## 🛠️ Daftar Fitur (12-in-1 Tools)

1. **JSON Formatter & Validator**: Format indentasi (2/4 spasi), persingkat (minify), validasi sintaksis, serta tree view interaktif.
2. **Base64 Codec**: Encode teks biasa ke Base64 dan decode Base64 kembali ke teks biasa.
3. **URL Codec**: Percent-encoding/decoding untuk komponen URL dan full URL, dilengkapi fitur parser query string.
4. **Regex Tester**: Uji regex secara langsung (live matching) dengan highlight pencocokan warna dan grup tangkapan (capture groups).
5. **Hash Generator**: Bikin hash SHA-1, SHA-256, SHA-384, dan SHA-512 secara cepat di sisi klien menggunakan Web Crypto API.
6. **Color Picker & Converter**: Pilih warna, konversi HEX, RGB, HSL, RGBA secara real-time, plus generator palet warna acak.
7. **JWT Decoder**: Bedah token JSON Web Token untuk melihat header, payload (iat, exp), dan status kedaluwarsa secara instan.
8. **Timestamp Converter**: Konversi Unix timestamp ke waktu lokal/UTC/ISO 8601 dan sebaliknya, dilengkapi penanda waktu real-time.
9. **Markdown Preview**: Editor Markdown interaktif dengan render HTML real-time untuk penulisan cepat dokumentasi.
10. **Lorem Ipsum Generator**: Hasilkan teks placeholder dalam bentuk kata, kalimat, atau paragraf secara acak untuk mockup.
11. **Password Generator**: Buat kata sandi acak yang aman dengan parameter panjang, kombinasi simbol, angka, huruf besar/kecil, dan indikator kekuatan password.
12. **Text Diff Viewer**: Bandingkan dua versi teks secara berdampingan untuk melihat perbedaan baris (ditambahkan/dihapus/sama).

---

## 🚀 Cara Pakai (Tanpa Build Step)

1. **Menggunakan Single HTML**:
   - Cukup unduh file `index.html` dari link di atas.
   - Klik ganda (double click) file `index.html` di komputer atau HP Anda untuk membukanya langsung di browser.
   - Tidak perlu menjalankan server lokal (`npm install` atau `live-server`). Zero dependencies!

2. **Menggunakan Versi ZIP**:
   - Unduh file `devtoolkit-pro.zip`.
   - Ekstrak file tersebut ke folder lokal Anda.
   - Buka `index.html` hasil ekstrak dengan browser kesayangan Anda.

---

## 🧪 Hasil Pengujian (Quality Gates)

Semua pemeriksaan kualitas (Quality Gates) otomatis telah berhasil dijalankan sebelum perilisan:
- **Format Check**: PASS (Self-contained HTML, no external script dependencies)
- **Syntax Check**: PASS (Tag balance validated)
- **Runtime Test**: PASS (HTML structure verified, file size: ~55 KB)
- **Edge Case Check**: PASS (Live tests on regex patterns, JWT parser, base64 errors handled)
