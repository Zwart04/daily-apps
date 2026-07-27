# Warkah — Time-Locked Digital Surat

## Masalah
Banyak orang ingin menulis surat digital untuk dibaca di masa depan — ulang tahun
anak ke-18, anniversary pernikahan, surat untuk diri sendiri 10 tahun lagi. Solusi
yang ada (FutureMe, Letter To Future Self) butuh registrasi akun, mengirim data
ke server pihak ketiga, dan hasil akhirnya kurang personal/indah.

## Target Pengguna
- Orang tua yang ingin menulis surat untuk anaknya yang akan dibaca saat dewasa
- Pasangan yang ingin menulis surat di hari pernikahan untuk dibaca 5/10/25 tahun lagi
- Seseorang yang menulis surat untuk dirinya sendiri di masa depan
- Guru/sahabat yang ingin meninggalkan pesan bermakna

## Kenapa Solusi yang Ada Belum Cukup
- FutureMe.org: butuh akun, email, data di server mereka
- Aplikasi catatan: tidak ada fitur "time-lock", tidak ada countdown
- Tool lain: butuh server, rumit, atau hasil jelek

## Fitur Inti MVP
1. Form pembuatan surat: judul, pengirim, penerima, pesan, tanggal buka
2. URL yang bisa dibagikan — semua data dienkode di URL (zero server)
3. Mode terkunci: tampilkan countdown timer yang elegan
4. Mode terbuka: tampilkan surat dengan tipografi indah ala surat sungguhan
5. Dukungan mode gelap/terang
6. Bisa di-print
7. 100% browser-based, zero server, zero login, zero dependency eksternal

## Tech Stack
- Single HTML file (no build step, no framework)
- Vanilla CSS dengan custom properties untuk theming
- Vanilla JavaScript
- Data encoding: JSON → UTF-8 → Base64 → URL hash
- Zero npm packages, zero CDN, zero backend
