# Warkah — Surat Digital untuk Masa Depan

**Warkah** adalah tool web 100% gratis untuk menulis surat digital yang hanya bisa dibuka di tanggal tertentu. Zero server, zero login, zero iklan.

Buat surat → dapat link → bagikan ke penerima. Link berisi data surat yang dienkripsi di URL, jadi tidak perlu server atau database. Surat akan menampilkan countdown sampai waktunya tiba, lalu otomatis terbuka.

## Fitur

- **Time-locked**: surat hanya bisa dibaca setelah tanggal yang ditentukan
- **Countdown elegan**: tampilkan hitungan mundur hari, jam, menit, detik
- **Tampilan surat indah**: tipografi serif, layout ala surat sungguhan
- **Cetak**: tombol cetak untuk menyimpan surat sebagai PDF
- **Mode gelap/terang**: otomatis mengikuti sistem
- **100% browser**: semua data di URL, tidak ada server
- **Responsif**: bekerja di HP, tablet, dan desktop
- **Open source**: MIT license

## Cara Pakai

1. Buka [zwart04.github.io/warkah](https://zwart04.github.io/warkah)
2. Isi judul, nama pengirim, nama penerima, pesan, dan tanggal buka
3. Klik "Buat Link Surat"
4. Salin link dan bagikan ke penerima via WhatsApp, email, atau media sosial
5. Penerima buka link — lihat countdown sampai tanggal yang ditentukan
6. Setelah tanggal tiba, surat otomatis terbuka dan bisa dicetak

## Contoh Penggunaan

- **Orang tua** menulis surat untuk anak yang baru lahir, dibuka saat ulang tahun ke-18
- **Pasangan** menulis surat di hari pernikahan, dibuka 10 tahun lagi
- **Sahabat** meninggalkan pesan untuk sahabatnya yang akan merantau
- **Untuk diri sendiri** — menulis goals dan harapan, dibuka setahun lagi

## Tech Stack

- Single HTML file (zero build step, zero framework)
- Vanilla CSS dengan custom properties (theming light/dark)
- Vanilla JavaScript murni
- Data encoding: JSON → UTF-8 → Base64URL → URL hash fragment
- Zero npm, zero CDN, zero backend, zero dependency

## Kenapa Ini Ada?

FutureMe.org dan sejenisnya butuh registrasi akun dan mengirim data ke server pihak ketiga. Warkah menyelesaikan masalah yang sama dengan pendekatan yang lebih privasi — data tetap di link, tidak pernah menyentuh server. Cukup HTML statis yang bisa di-host di GitHub Pages atau server mana pun.

## Development

Repository ini hanya berisi satu file `index.html`. Clone, buka langsung di browser, atau serve dengan:

```bash
python3 -m http.server 8080
```

## Lisensi

MIT &mdash; lihat file [LICENSE](LICENSE).

---

Dibuat oleh [Zwart04](https://github.com/Zwart04). Terinspirasi dari kebutuhan untuk meninggalkan pesan bermakna bagi orang tersayang di masa depan.
