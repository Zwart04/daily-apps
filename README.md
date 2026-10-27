# Daily Workspace

Satu aplikasi untuk merencanakan proyek, mengerjakan tugas, membuat karya, dan menjalankan operasi. Seluruh fitur menggunakan satu akun dan satu alamat:

**[Buka Daily Workspace](https://daily-apps-app.zwart.qzz.io/)**

## Alur penggunaan

1. Daftar atau masuk. Password diverifikasi server; simpan kode pemulihan yang ditampilkan sekali.
2. Buat ruang kerja kosong. Undang anggota sebagai editor atau viewer sesuai kebutuhan.
3. Buat proyek dan tentukan hasilnya. Uraikan menjadi tugas, pindahkan status pada papan tugas, dan mulai sesi fokus. Waktu disahkan server.
4. Gunakan alat kerja atau catatan operasional. Tautkan hasil yang sudah disimpan ke proyek, sehingga tugas, waktu, dan hasil dapat dilihat bersama.
5. Pantau agenda dan laporan lintas bidang. Cari catatan dari satu kolom pencarian, ekspor seluruh ruang, atau pulihkan catatan dari Sampah.

Tidak ada akun demo, seed produksi, angka dashboard buatan, harga simulasi, atau jawaban AI pengganti ketika provider gagal. Ruang baru benar-benar kosong.

## Kemampuan dalam aplikasi yang sama

- **Rencana:** proyek, papan tugas, fokus, kebiasaan/check-in, rutinitas, target, anggaran, perjalanan, surat terenkripsi, dokumen, formulir publik, kosakata.
- **Studio:** pengolah audio/WAV, trim video/WebM, crop/teks gambar, library aset; editor kode dan assertion di sandbox; editor tile/entity dan shader WebGL.
- **Belajar:** kursus, materi, flashcard, jadwal review, kuis dinilai server, riwayat nilai.
- **Operasi:** stok dan pesanan dengan alur konfirmasi → invoice → pembayaran tercatat → pengiriman, layanan/booking/pekerjaan/rute, data klinik, perkara/dokumen/tenggat, lokasi/sensor/pengukuran/pertanian, transaksi dan portofolio pasar.
- **Bersama:** satu login, ruang tim, peran, pencarian, agenda, tautan hasil ke proyek, audit, sampah, backup JSON/CSV, dan Workers AI.

Bidang kerja merupakan bagian native aplikasi. Tidak ada iframe produk lain atau menu pindah aplikasi. Jenis catatan dengan nama sama di bidang berbeda memiliki ruang data sendiri agar migrasi tidak menimpa data.

## Menjalankan dan memeriksa

Node.js 24 dan Python 3 diperlukan.

```sh
npm ci
npm test
npm run test:cli
npm run build
```

Untuk pengembangan backend lokal, gunakan konfigurasi terpisah dan database lokal; jangan gunakan `--remote` terhadap produksi untuk pengujian. `npm run dev` menjalankan frontend. Operasi akun/data memerlukan backend Cloudflare atau proxy pengembangan yang diarahkan ke backend lokal, bukan autentikasi tiruan.

## Hosting dan data

Frontend Worker `zwart04-daily-apps` memanggil backend privat `zwart04-platform-v2` melalui service binding. Cloudflare D1 menyimpan akun, session, catatan, audit, dan tautan proyek. Source backend sekarang berada di `platform/` pada repo ini. Lihat [arsitektur](docs/UNIFIED-WORKSPACE.md), [deployment dan pemulihan](docs/DEPLOYMENT.md), serta [rencana penggabungan](plans/REBUILD-PLAN.md).

Password dan kode pemulihan menggunakan secret `PEPPER`. **Jangan mengganti secret produksi ketika deploy atau memulihkan source.** Surat terenkripsi juga bergantung pada secret yang sama. Source backup di GitHub tidak berisi data pribadi atau secret tersebut.

Anggota satu ruang memiliki akses ke seluruh bidangnya sesuai peran. Gunakan ruang berbeda untuk tim yang berbeda. Ruang lama hanya digabung otomatis jika pemilik serta daftar anggota/perannya identik. ID dan isi catatan lama tetap dipertahankan.

## Batas yang terlihat jelas

- Media diproses di perangkat. Metadata aset ada di D1; isi berkas besar berada di IndexedDB browser pengunggah. Unduh berkas asli/hasil sebelum membersihkan browser atau mengganti perangkat. Aplikasi tidak mengaku berkas lokal sudah diunggah ke cloud.
- Ekspor video menggunakan MediaRecorder/WebM, maksimal lima menit per klip, dan membutuhkan tab aktif. Dukungan codec, suara sistem, serta WebGL mengikuti browser. Pembacaan teks sistem tidak menjanjikan ekspor suaranya.
- Harga BTC/ETH/SOL berasal dari Coinbase, kurs dari Frankfurter/ECB. Provider yang gagal menampilkan kegagalan; tidak diganti nilai contoh.
- Pembayaran adalah catatan pembayaran yang benar-benar diterima pengguna, bukan payment gateway. Rute menggunakan jarak garis lurus, bukan kondisi jalan. Sensor membutuhkan perangkat dan API key nyata.
- AI memiliki batas 5 pesan/akun/hari dan 40 pesan aplikasi/hari. Hosting memakai layanan gratis Cloudflare; batas provider tetap berlaku. Tidak ada layanan berbayar yang diaktifkan oleh rebuild ini.

## Riwayat dan backup source

Repo ini menggantikan katalog dan sepuluh repo produk lama. [Recovery release](https://github.com/Zwart04/daily-apps/releases/tag/workspace-consolidation-backup) pada repo ini menyimpan arsip lama dengan 50 riwayat Git serta 12 snapshot sebelum penggabungan, metadata repo, checksum, dan laporan uji restore. Ini adalah snapshot yang sebagian saling beririsan, bukan 62 repo berbeda. Seluruh snapshot diuji dengan clone dan `git fsck` sebelum penghapusan repo sumber. Data pengguna tetap berada pada D1 yang sama; source archive publik tidak memuat database produksi.
