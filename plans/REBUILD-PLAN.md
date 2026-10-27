# Rencana penggabungan 27 Oktober 2026

Target: satu repository **Zwart04/daily-apps**, satu aplikasi Daily Workspace, satu login pada daily-apps-app.zwart.qzz.io. Semua 11 produk dilebur menjadi bidang dan alat native dalam ruang kerja.

## Tahapan dan kriteria selesai

1. **Inventaris:** cocokkan pemilik/public/default HEAD pada 12 repo yang diizinkan. Ambil baseline D1, bookmark pemulihan, dan daftar domain. Jangan menyentuh repo private, agenmini, zwartos, ZwartGuard, rakaat-counter, atau akun lain.
2. **Backup:** pindahkan recovery archive lama dengan checksum asli, simpan 12 bundle terbaru dan metadata GitHub. Uji clone/restore/fsck semua snapshot. Upload satu recovery asset ke repo yang dipertahankan; cocokkan digest dari server.
3. **Backend:** pertahankan akun, PEPPER, database, schema domain, dan ID lama; tambahkan akar ruang, bidang internal, tautan proyek, agenda/pencarian, dan timer server. Hak akses akar berlaku untuk semua bidang.
4. **Frontend:** bangun ulang satu shell responsif, auth/recovery/onboarding, proyek-tugas-fokus-hasil, dashboard nyata, agenda/pencarian/laporan terpadu, katalog alat native, dan alur operasi yang jelas. Hilangkan launcher produk dan iframe.
5. **Verifikasi:** test keamanan/workflow seluruh bidang; staging D1 terpisah; uji browser desktop/mobile dan alat penting; tanpa seed atau akun uji di produksi. Periksa CI.
6. **Produksi:** migrasi additive dan metadata sesuai ACL, cocokkan fingerprint record dan hash credential; deploy backend/antarmuka; arahkan alias lama ke satu origin sambil menjaga API ingestion.
7. **Penghapusan terakhir:** hanya setelah source recovery terunduh/terverifikasi, fitur teruji, data tetap utuh, HTTPS aktif, dan CI lulus, hapus 11 repo yang disetujui. Periksa status 404. Bersihkan resource staging serta file kerja sementara milik tugas ini.

## Repo yang dipertahankan

- Zwart04/daily-apps

## Daftar penghapusan yang disetujui pengguna

- Zwart04/zwart04-projects
- Zwart04/daganghub
- Zwart04/renderforge
- Zwart04/tutormind
- Zwart04/servora
- Zwart04/aquapure
- Zwart04/clinic-os
- Zwart04/legalbot-garuda
- Zwart04/codeforgeme
- Zwart04/gridcraft
- Zwart04/stockgenie

Bukti hasil tiap tahap disimpan sebagai laporan terpisah di folder ini. Tidak menganggap tahap selesai sebelum bukti ada.
