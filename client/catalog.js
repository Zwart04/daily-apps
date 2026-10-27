import { PRODUCTS } from "../platform/definitions.js";
export const AREA_LABELS = {
  "daily-apps": "Pribadi & harian",
  daganghub: "Penjualan & persediaan",
  renderforge: "Produksi media",
  tutormind: "Pendidikan",
  servora: "Layanan lapangan",
  aquapure: "Lingkungan & pertanian",
  "clinic-os": "Pelayanan klinik",
  "legalbot-garuda": "Perkara & dokumen",
  codeforgeme: "Pengembangan software",
  gridcraft: "Desain interaktif",
  stockgenie: "Portofolio pasar",
};
export const GROUPS = [
  {
    name: "Rencanakan",
    description: "Rencana harian, kebiasaan, perjalanan, dan catatan.",
    areas: ["daily-apps"],
  },
  {
    name: "Buat & pelajari",
    description: "Dari ide menjadi materi, media, kode, dan karya interaktif.",
    areas: ["renderforge", "codeforgeme", "gridcraft", "tutormind"],
  },
  {
    name: "Jalankan operasi",
    description: "Pesanan, pekerjaan, layanan, lingkungan, dan keuangan.",
    areas: [
      "daganghub",
      "servora",
      "aquapure",
      "clinic-os",
      "legalbot-garuda",
      "stockgenie",
    ],
  },
];
export const TOOLS = [
  [
    "daily-apps",
    "day-view",
    "Rencana hari ini",
    "Susun prioritas, kebiasaan, dan rutinitas.",
  ],
  [
    "daily-apps",
    "daily-tools",
    "Dokumen & utilitas",
    "Markdown, formulir publik, pengolah data, dan alat sehari-hari.",
  ],
  [
    "renderforge",
    "creative-studio",
    "Studio media",
    "Olah gambar, audio, dan video dari berkas Anda.",
  ],
  [
    "codeforgeme",
    "code-studio",
    "Editor & pengujian kode",
    "Tulis, jalankan di sandbox, uji, dan ekspor proyek.",
  ],
  [
    "gridcraft",
    "level-editor",
    "Editor level",
    "Rancang peta tile, entitas, lalu ekspor hasilnya.",
  ],
  [
    "gridcraft",
    "shader-editor",
    "Editor shader",
    "Tulis GLSL dan lihat hasil render langsung.",
  ],
  [
    "tutormind",
    "learn",
    "Ruang belajar",
    "Materi, kartu ulasan, serta kuis yang dinilai server.",
  ],
  [
    "daily-apps",
    "word-practice",
    "Latihan kosakata",
    "Ulangi kartu dari daftar kata milik Anda.",
  ],
  [
    "daganghub",
    "pricing",
    "Perencanaan harga",
    "Hitung margin dan titik impas dari biaya nyata.",
  ],
  [
    "servora",
    "route-planner",
    "Rute pekerjaan",
    "Susun urutan kunjungan dari koordinat pekerjaan.",
  ],
  [
    "aquapure",
    "field-map",
    "Peta lapangan",
    "Lihat lokasi dan titik pengukuran Anda.",
  ],
  [
    "aquapure",
    "ingestion",
    "Hubungkan sensor",
    "Terima pengukuran perangkat melalui API berkunci.",
  ],
  [
    "stockgenie",
    "market",
    "Pantau portofolio",
    "Harga pasar langsung dan posisi dari transaksi Anda.",
  ],
  [
    "codeforgeme",
    "dev-tools",
    "Utilitas developer",
    "Format data, regex, transformasi, dan dokumen.",
  ],
  [
    "renderforge",
    "assistant",
    "Asisten pekerjaan",
    "Bahas konteks yang Anda kirim dengan Workers AI.",
  ],
].map(([area, key, title, description]) => ({
  area,
  key,
  title,
  description,
  module: PRODUCTS[area].modules.find((m) => m.key === key),
}));
export const FLOWS = {
  daganghub: [
    ["products", "1. Produk & stok"],
    ["customers", "2. Pelanggan"],
    ["orders", "3. Pesanan → invoice → pembayaran → pengiriman"],
    ["reports", "4. Laporan"],
  ],
  servora: [
    ["services", "1. Jenis layanan"],
    ["customers", "2. Pelanggan"],
    ["bookings", "3. Booking → pekerjaan"],
    ["jobs", "4. Pelaksanaan & rute"],
  ],
  "clinic-os": [
    ["patients", "1. Pasien"],
    ["appointments", "2. Jadwal → kunjungan"],
    ["encounters", "3. Pemeriksaan"],
    ["prescriptions", "4. Resep & tindak lanjut"],
  ],
  tutormind: [
    ["courses", "1. Kursus"],
    ["lessons", "2. Materi"],
    ["quizzes", "3. Kuis"],
    ["learn", "4. Belajar & penilaian"],
  ],
  aquapure: [
    ["sites", "1. Lokasi"],
    ["sensors", "2. Perangkat"],
    ["ingestion", "3. Hubungkan sensor"],
    ["water_samples", "4. Pengukuran & peringatan"],
  ],
  renderforge: [
    ["projects", "1. Proyek produksi"],
    ["assets", "2. Aset"],
    ["creative-studio", "3. Studio media"],
    ["publishing", "4. Jadwal publikasi"],
  ],
  codeforgeme: [
    ["projects", "1. Proyek kode"],
    ["files", "2. Sumber"],
    ["code-studio", "3. Editor & pengujian"],
    ["releases", "4. Rilis"],
  ],
  gridcraft: [
    ["projects", "1. Karya interaktif"],
    ["level-editor", "2. Rancang level"],
    ["shader-editor", "3. Shader"],
    ["versions", "4. Versi"],
  ],
  "legalbot-garuda": [
    ["clients", "1. Klien"],
    ["matters", "2. Perkara"],
    ["documents", "3. Dokumen"],
    ["deadlines", "4. Tenggat"],
  ],
  stockgenie: [
    ["holdings", "1. Saldo awal"],
    ["transactions", "2. Transaksi"],
    ["market", "3. Pantau harga"],
    ["reports", "4. Laporan"],
  ],
};
