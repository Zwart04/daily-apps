# Penggabungan selesai

Aplikasi: https://apps.zwart.my.id/

Domain diperbarui atas permintaan pengguna; seluruh 50 alamat lama di `zwart.qzz.io` kini menjadi alias. Akun, data, dan backend tetap sama.
Repo tunggal: https://github.com/Zwart04/daily-apps
Recovery: https://github.com/Zwart04/daily-apps/releases/tag/workspace-consolidation-backup

- Sebelas repo yang disetujui dihapus; masing-masing diperiksa 404 setelah backup source dapat diunduh dan checksum cocok.
- Lima puluh hostname tetap berfungsi: halaman lama mengarah ke satu origin, API tetap diteruskan.
- Dua akun, seluruh isi record dan hash credential lama tetap utuh. Empat ruang internal lama terkait ke dua akar sesuai pemilik/ACL, tanpa menambah record contoh.
- Dua puluh tiga test Node dan tiga test CLI lulus; build produksi dan audit dependensi lulus. CI GitHub juga lulus.
- Registrasi, recovery, proyek/tugas/fokus, navigasi desktop/mobile, semua 15 halaman alat, sandbox kode, audio/video export, tile save, shader rendering, sensor, kuis, kurs, pasar, dan Workers AI diperiksa di staging terpisah.
- Dua belas repo private serta seluruh 22 repo di luar daftar tetap memiliki metadata yang sama. Source private tidak dibaca atau diubah.
- Worker frontend lama dan seluruh lingkungan staging dihapus. Backend produksi, secret, database, serta resource di luar tugas tetap dipertahankan.
- Snapshot source yang saling beririsan: 50 dalam arsip legacy + 12 sebelum penggabungan; seluruh 62 snapshot lolos clone/restore/git fsck. Satu ZIP recovery tersedia di release dan folder Backup lokal.

Bukti rinci tersedia dalam JSON di folder ini. Screenshot staging memuat fixture pengujian terisolasi; fixture tersebut tidak dipindahkan ke produksi. Media besar tetap bersifat lokal di browser pengunggah, sesuai keterangan library aset.
