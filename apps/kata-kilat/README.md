# Kata Kilat

**Tebak kata Bahasa Indonesia dari definisinya secepat mungkin.**

Kata Kilat adalah game kuis kata Bahasa Indonesia yang dimainkan langsung di browser. Pemain membaca definisi sebuah kata, lalu mengetikkan jawaban sebelum waktu habis. Makin cepat jawab, makin banyak poin yang didapat. Cocok untuk semua kalangan — pelajar, orang dewasa, atau siapa saja yang ingin mengasah kosakata Bahasa Indonesia.

## Apa ini

Game tebak kata berbasis browser, satu file HTML, tidak perlu instalasi, tidak perlu internet (setelah dibuka pertama kali). Dimainkan langsung di tab browser.

## Cara Pakai

1. Unduh file `index.html`
2. Buka file tersebut di browser (klik dua kali, atau drag ke browser)
3. Klik tombol "Mulai Bermain"
4. Baca definisi yang tampil — ketik jawabanmu sebelum 30 detik habis
5. Tekan Enter atau klik "Jawab" untuk mengumpulkan jawaban

## Fitur

- 63 kata dalam bank soal dari 6 kategori: Alam, Hewan, Makanan, Benda, Sifat, Profesi
- Timer visual 30 detik dengan indikator lingkaran yang berubah warna
- Sistem poin berbasis kecepatan: jawab cepat = poin lebih banyak (max ~90 poin per soal)
- Streak bonus: 3 jawaban benar berturut-turut = +30 poin ekstra
- Tombol Petunjuk: tampilkan huruf pertama kata (mengurangi 20 poin)
- Skor tersimpan di browser (top 5 high scores via localStorage)
- Review semua soal setelah game selesai
- Desain dark mode yang nyaman di mata, responsif untuk layar kecil dan besar
- Tidak perlu internet setelah pertama kali dibuka (semua aset via CDN saat load awal)

## Kenapa berguna

Belajar kosakata Bahasa Indonesia sering terasa membosankan. Kata Kilat mengubahnya menjadi game yang menyenangkan — ada tekanan waktu, ada streak, ada skor tinggi yang ingin dipecahkan. Cocok dimainkan saat istirahat, buat latihan sebelum ujian, atau sekadar mengisi waktu sambil mengasah pengetahuan bahasa.

## Quick Start

```bash
# Unduh dan buka langsung
curl -L -o kata-kilat.html https://raw.githubusercontent.com/[username]/20260706-kata-kilat/main/index.html
# Kemudian buka kata-kilat.html di browser
```

Atau: klon repo ini, buka `index.html` di browser.

## Kategori Soal

| Kategori | Jumlah | Contoh |
|----------|--------|--------|
| Alam | 12 | rimba, kawah, telaga, gletser |
| Hewan | 12 | kancil, bekantan, dugong, komodo |
| Makanan | 12 | rendang, klepon, gudeg, pempek |
| Benda | 12 | cobek, kendi, mercusuar, kompas |
| Sifat | 6 | bijaksana, dermawan, serakah |
| Profesi | 6 | nelayan, arsitek, pandai besi |

## Arsitektur

Satu file HTML self-contained:
- HTML5 semantik
- CSS murni dengan custom properties (CSS variables)
- JavaScript vanilla (tidak ada framework)
- Lucide Icons via CDN untuk ikon
- Google Fonts (Plus Jakarta Sans) via CDN
- localStorage untuk penyimpanan skor

## Design Philosophy

1. **Zero friction** — Satu klik langsung main. Tidak ada login, instalasi, atau setup
2. **Offline-first** — Semua logika di browser, tidak ada server
3. **Belajar sambil main** — Definisi yang digunakan mengandung informasi edukatif

## License

MIT
