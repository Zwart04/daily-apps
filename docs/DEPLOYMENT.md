# Deployment dan pemulihan

## Produksi

Konfigurasi frontend: `wrangler.jsonc`. Backend privat: `platform/wrangler.jsonc`. Periksa account ID, domain, service binding, dan ID D1 sebelum menjalankan perintah.

```sh
npm ci
npm test
npm run test:cli
npm run build
npx wrangler deploy --config platform/wrangler.jsonc
npx wrangler deploy --config wrangler.jsonc
```

Schema baru boleh memakai `platform/schema.sql` **hanya pada database kosong**. Untuk database produksi lama, gunakan hanya migrasi additive `platform/migrations/003_unified_workspace.sql`, sesudah snapshot serta bookmark D1 diambil. Jangan mengganti binding DB atau PEPPER ketika memperbarui Worker produksi.

## Pemulihan source

Unduh asset recovery dari release `workspace-consolidation-backup` di Zwart04/daily-apps dan checksum yang menyertainya. Verifikasi SHA256 ZIP sebelum mengekstrak. Folder `repositories/` berisi snapshot saat konsolidasi. ZIP legacy di dalamnya berisi lima puluh snapshot terdahulu; ekstrak terpisah.

```sh
git clone repositories/servora.bundle restored-servora
git -C restored-servora fsck --full
```

Bundle mempertahankan histori/ref Git; metadata GitHub disimpan sebagai JSON. Mengembalikan repository yang dihapus perlu membuat repo baru dan push ref dari mirror. Jangan mengunggah data privat atau secret ke recovery release publik.

## Pemulihan data produksi

Data tetap berada di database D1 yang sama. Cloudflare D1 Time Travel dan snapshot privat sebelum migrasi merupakan jalur pemulihan data. Bookmark disimpan lokal di `.migration-private/production-before.json` dengan mode 600; tidak dipublikasikan. Free tier Time Travel memiliki retensi terbatas. Snapshot lokal bukan pengganti backup jangka panjang; ekspor data dari Pengaturan secara berkala. Kembalikan Worker version sebelumnya dan binding domain dari manifest sebelum mencoba pemulihan database. Jangan memakai snapshot source publik untuk menimpa data produksi.

## Privasi dan batas migrasi

Isi IndexedDB di browser/perangkat pengguna tidak dapat dipindah dari server. Unduh aset lokal sebelum membersihkan perangkat atau browser. Metadata D1 tetap tersimpan. Tim dengan anggota berbeda tetap menjadi ruang terpisah, namun menggunakan aplikasi dan akun yang sama.

Lingkungan staging harus dihapus setelah verifikasi: Worker stage frontend/backend dan database dengan ID yang tercatat pada manifest staging. Jangan menghapus database atau Worker lain berdasarkan pencocokan nama umum.
