# Arsitektur ruang terpadu

## Satu identitas dan satu antarmuka

Frontend React berada di satu origin. Seluruh `/api` memakai cookie session HttpOnly, Secure, SameSite=Lax dan token CSRF. Cookie tidak diperluas ke seluruh domain. Alias situs lama mengalihkan halaman ke origin yang sama. Request API pada alias tetap diteruskan tanpa mengubah metode/body agar perangkat sensor lama dapat terus mengirim.

Sidebar berisi pekerjaan pengguna: Hari ini, Proyek, Papan tugas, Agenda, Alat kerja, Data & operasi, Laporan. Editor dan alat ditampilkan sebagai komponen native, bukan iframe dari situs lain. Proyek menghubungkan tugas, waktu fokus yang dihitung server, serta catatan hasil dari bidang mana pun dalam ruang yang sama.

## Penyimpanan yang kompatibel

`workspaces` dengan product `daily-apps` adalah akar ruang tim. `workspace_areas` memetakan bidang ke ID ruang internal. Tabel dan ID record lama tidak dipindah atau ditulis ulang. Namespace seperti `projects` pada media, kode, desain, dan akar tetap terpisah. `workspace_project_links` menghubungkan record hasil tanpa menduplikasinya.

Router terlebih dahulu memeriksa keanggotaan akar, lalu memilih schema bidang dari database. Klien tidak dapat menentukan produk backend melalui header untuk membuka data lain. Cache anggota ruang internal disamakan dengan peran akar setelah otorisasi; cache lama tidak dapat mengalahkan pencabutan akses pada akar. Perubahan nama/anggota dilakukan pada akar saja.

## Migrasi

Migrasi SQL 003 bersifat menambah tabel dan index. Migrasi metadata membuat akar dengan daftar anggota dan peran yang identik. Ruang dengan ACL berbeda tidak digabung otomatis. Semua record, ID ruang lama, kunci sensor, hash password, recovery hash, dan secret PEPPER dipertahankan. Fingerprint record sebelum/sesudah diverifikasi. Script migrasi dapat dilanjutkan jika terputus menggunakan manifest privat yang sama.

## Kejujuran data

Root baru mengaktifkan semua bidang tanpa membuat record contoh. Ringkasan menghitung data D1. Waktu fokus dihitung dari waktu server, bukan angka dari browser. Provider AI/pasar yang gagal tidak memberikan respons sintetis. Ekspor dan pencarian hanya menjangkau akar dan bidang yang terkait dengan akar tersebut. Viewer tidak menerima kunci jawaban kuis atau isi surat yang belum terbuka.

## Pengujian

Test backend memakai SQLite in-memory dengan schema yang sama dan fixture terisolasi. Staging memiliki database dan pepper sendiri; tidak menggunakan database produksi. Uji browser memeriksa registrasi, konfirmasi penyimpanan recovery, pembuatan ruang kosong, proyek/tugas/fokus, serta navigasi desktop dan mobile. Snapshot hasil uji di `plans/` diberi label staging. Data uji tidak disalin ke produksi.
