# Formie — Mini PRD v1

## Masalah
Orang non-teknis yang generate website pakai AI (ChatGPT, Claude, v0, Bolt) hampir selalu butuh form — contact form, signup form, feedback form, survey — tapi mereka gak bisa nulis HTML form yang bener (input types, labels, validation, accessibility). Kebanyakan form builder yang ada (Google Forms, Typeform, Tally) terkunci di platform mereka sendiri, sedangkan library kayak Formeo/VvvebJs butuh setup teknis.

## Target Pengguna
Sama kayak Retouch & Thema: non-teknis yang generate website pakai AI. Mereka butuh form builder drag-and-drop gratis, zero-install (buka browser langsung bisa), yang outputnya kode HTML siap paste ke project mereka.

## Kenapa Beda dari yang Sudah Ada
- Gratis total, no signup, no server, no backend
- Satu file HTML, buka browser langsung pakai (bisa offline)
- Output clean standalone HTML form — bukan terikat platform
- Drag-and-drop visual, gak perlu ngerti kode
- Dark theme built-in
- Target: non-teknis (bukan library untuk developer)
- Formeo/VvvebJs butuh setup/library; HeyForm butuh backend; jQuery formBuilder butuh jQuery

## Fitur Inti MVP
1. **Field palette** — sidebar dengan daftar field type: text, email, textarea, select (dropdown), checkbox, radio, number, url, tel, date, file upload, password, submit button
2. **Drag to canvas** — seret field dari palette ke form canvas (HTML5 Drag API)
3. **Edit field properties** — klik field di canvas: edit label, placeholder, required toggle, options (untuk select/checkbox/radio), button text
4. **Reorder fields** — drag field di canvas untuk mindahin urutan
5. **Delete / Duplicate** — hapus atau duplikasi field
6. **Preview mode** — toggle edit/preview, liat form kayak pengguna
7. **Export HTML** — download kode HTML form clean (dengan inline styles, standalone)
8. **Import JSON** — simpan/load form structure biar gak ilang
9. **Dark theme** — sama kayak Retouch
10. **Undo/Redo** — 30 langkah undo

## Tech Stack
- Vanilla JavaScript (zero dependencies, no build step)
- HTML5 Drag and Drop API
- Satu file `index.html`
- Tailwind CSS v4 CDN (sama kayak Retouch)
- Deploy ke GitHub Pages

## Fitur NON-MVP (post-v1)
- Conditional logic (show/hide field based on value)
- Multi-page / wizard form
- File upload to cloud
- Email integration (Formspree, Web3Forms)
- Custom CSS theming
- i18n
