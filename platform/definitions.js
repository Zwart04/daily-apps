export const PRODUCTS = {
  "daily-apps": {
    "accent": "#93c840",
    "currency": "IDR",
    "tagline": "Make room for a better day.",
    "modules": [
      {
        "key": "day-view",
        "label": "Rencana hari",
        "tool": "day-planner",
        "fields": [],
        "statuses": []
      },
      {
        "key": "tasks",
        "label": "Tugas",
        "fields": [
          {
            "key": "name",
            "label": "Nama / judul",
            "type": "text",
            "required": true
          },
          {
            "key": "date",
            "label": "Tanggal",
            "type": "date",
            "required": true
          },
          {
            "key": "priority",
            "label": "Prioritas",
            "type": "select",
            "options": [
              "low",
              "normal",
              "high"
            ]
          },
          {
            "key": "notes",
            "label": "Catatan",
            "type": "textarea"
          }
        ],
        "statuses": [
          "todo",
          "doing",
          "done"
        ]
      },
      {
        "key": "habits",
        "label": "Kebiasaan",
        "fields": [
          {
            "key": "name",
            "label": "Nama / judul",
            "type": "text",
            "required": true
          },
          {
            "key": "frequency",
            "label": "Frekuensi",
            "type": "select",
            "options": [
              "daily",
              "weekly"
            ]
          },
          {
            "key": "target",
            "label": "Target per minggu",
            "type": "number",
            "min": 1,
            "max": 7
          },
          {
            "key": "notes",
            "label": "Catatan",
            "type": "textarea"
          }
        ],
        "statuses": [
          "active",
          "archived"
        ]
      },
      {
        "key": "checkins",
        "label": "Check-in",
        "fields": [
          {
            "key": "name",
            "label": "Nama / judul",
            "type": "text",
            "required": true
          },
          {
            "key": "habit_id",
            "label": "Kebiasaan",
            "type": "ref",
            "ref": "habits",
            "required": true
          },
          {
            "key": "date",
            "label": "Tanggal",
            "type": "date",
            "required": true
          },
          {
            "key": "notes",
            "label": "Catatan",
            "type": "textarea"
          }
        ],
        "statuses": [
          "completed",
          "missed"
        ]
      },
      {
        "key": "routines",
        "label": "Rutinitas",
        "fields": [
          {
            "key": "name",
            "label": "Nama / judul",
            "type": "text",
            "required": true
          },
          {
            "key": "steps",
            "label": "Langkah (satu per baris)",
            "type": "textarea",
            "required": true
          },
          {
            "key": "time",
            "label": "Jam mulai",
            "type": "time"
          },
          {
            "key": "notes",
            "label": "Catatan",
            "type": "textarea"
          }
        ],
        "statuses": [
          "active",
          "archived"
        ]
      },
      {
        "key": "routine_runs",
        "label": "Sesi rutinitas",
        "fields": [
          {
            "key": "name",
            "label": "Nama / judul",
            "type": "text",
            "required": true
          },
          {
            "key": "routine_id",
            "label": "Rutinitas",
            "type": "ref",
            "ref": "routines",
            "required": true
          },
          {
            "key": "date",
            "label": "Tanggal",
            "type": "date",
            "required": true
          },
          {
            "key": "completed_steps",
            "label": "Indeks langkah selesai",
            "type": "json"
          }
        ],
        "statuses": [
          "active",
          "done"
        ]
      },
      {
        "key": "goals",
        "label": "Target",
        "fields": [
          {
            "key": "name",
            "label": "Nama / judul",
            "type": "text",
            "required": true
          },
          {
            "key": "target",
            "label": "Target angka",
            "type": "number",
            "min": 1
          },
          {
            "key": "current",
            "label": "Pencapaian",
            "type": "number",
            "min": 0
          },
          {
            "key": "unit",
            "label": "Satuan",
            "type": "text"
          },
          {
            "key": "deadline",
            "label": "Tenggat",
            "type": "date"
          }
        ],
        "statuses": [
          "active",
          "done"
        ]
      },
      {
        "key": "notes",
        "label": "Catatan",
        "fields": [
          {
            "key": "name",
            "label": "Nama / judul",
            "type": "text",
            "required": true
          },
          {
            "key": "body",
            "label": "Isi catatan",
            "type": "textarea",
            "required": true
          },
          {
            "key": "tags",
            "label": "Tag",
            "type": "text"
          }
        ],
        "statuses": [
          "active",
          "archived"
        ]
      },
      {
        "key": "budget",
        "label": "Anggaran",
        "fields": [
          {
            "key": "name",
            "label": "Nama / judul",
            "type": "text",
            "required": true
          },
          {
            "key": "date",
            "label": "Tanggal",
            "type": "date",
            "required": true
          },
          {
            "key": "type",
            "label": "Jenis",
            "type": "select",
            "options": [
              "income",
              "expense"
            ]
          },
          {
            "key": "amount",
            "label": "Jumlah",
            "type": "money"
          },
          {
            "key": "category",
            "label": "Kategori",
            "type": "text"
          },
          {
            "key": "notes",
            "label": "Catatan",
            "type": "textarea"
          }
        ],
        "statuses": [
          "active",
          "archived"
        ]
      },
      {
        "key": "trips",
        "label": "Perjalanan",
        "fields": [
          {
            "key": "name",
            "label": "Nama / judul",
            "type": "text",
            "required": true
          },
          {
            "key": "destination",
            "label": "Tujuan",
            "type": "text",
            "required": true
          },
          {
            "key": "start_date",
            "label": "Tanggal berangkat",
            "type": "date"
          },
          {
            "key": "end_date",
            "label": "Tanggal pulang",
            "type": "date"
          },
          {
            "key": "budget",
            "label": "Anggaran",
            "type": "money"
          },
          {
            "key": "notes",
            "label": "Catatan",
            "type": "textarea"
          }
        ],
        "statuses": [
          "planning",
          "booked",
          "active",
          "done"
        ]
      },
      {
        "key": "itinerary",
        "label": "Itinerary",
        "fields": [
          {
            "key": "name",
            "label": "Nama / judul",
            "type": "text",
            "required": true
          },
          {
            "key": "trip_id",
            "label": "Perjalanan",
            "type": "ref",
            "ref": "trips",
            "required": true
          },
          {
            "key": "start",
            "label": "Mulai",
            "type": "datetime",
            "required": true
          },
          {
            "key": "end",
            "label": "Selesai",
            "type": "datetime",
            "required": true
          },
          {
            "key": "location",
            "label": "Lokasi",
            "type": "text"
          },
          {
            "key": "cost",
            "label": "Biaya",
            "type": "money"
          },
          {
            "key": "notes",
            "label": "Catatan",
            "type": "textarea"
          }
        ],
        "statuses": [
          "active",
          "archived"
        ]
      },
      {
        "key": "letters",
        "label": "Surat terjadwal",
        "fields": [
          {
            "key": "name",
            "label": "Nama / judul",
            "type": "text",
            "required": true
          },
          {
            "key": "body",
            "label": "Isi surat",
            "type": "textarea",
            "required": true
          },
          {
            "key": "unlock_at",
            "label": "Buka pada",
            "type": "datetime",
            "required": true
          }
        ],
        "statuses": [
          "sealed"
        ]
      },
      {
        "key": "drafts",
        "label": "Dokumen & draft",
        "fields": [
          {
            "key": "name",
            "label": "Nama / judul",
            "type": "text",
            "required": true
          },
          {
            "key": "type",
            "label": "Jenis",
            "type": "select",
            "options": [
              "html",
              "form",
              "theme",
              "data",
              "text"
            ]
          },
          {
            "key": "content",
            "label": "Isi",
            "type": "textarea"
          }
        ],
        "statuses": [
          "active",
          "archived"
        ]
      },
      {
        "key": "forms",
        "label": "Form online",
        "fields": [
          {
            "key": "name",
            "label": "Nama / judul",
            "type": "text",
            "required": true
          },
          {
            "key": "description",
            "label": "Deskripsi",
            "type": "textarea"
          },
          {
            "key": "fields",
            "label": "Field form",
            "type": "json",
            "required": true
          }
        ],
        "statuses": [
          "draft",
          "published",
          "closed"
        ],
        "actions": [
          "publish-form"
        ]
      },
      {
        "key": "form_responses",
        "label": "Respons form",
        "fields": [
          {
            "key": "name",
            "label": "Nama / judul",
            "type": "text",
            "required": true
          },
          {
            "key": "form_id",
            "label": "Form",
            "type": "ref",
            "ref": "forms",
            "required": true
          },
          {
            "key": "answers",
            "label": "Jawaban",
            "type": "json"
          },
          {
            "key": "received_at",
            "label": "Waktu diterima",
            "type": "datetime"
          }
        ],
        "statuses": [
          "received"
        ]
      },
      {
        "key": "daily-tools",
        "label": "Alat kerja",
        "tool": "daily-tools",
        "fields": []
      },
      {
        "key": "calendar",
        "label": "Kalender",
        "tool": "calendar",
        "fields": []
      },
      {
        "key": "word_cards",
        "label": "Bank kata",
        "fields": [
          {
            "key": "name",
            "label": "Kata",
            "type": "text",
            "required": true
          },
          {
            "key": "definition",
            "label": "Definisi Anda",
            "type": "textarea",
            "required": true
          }
        ],
        "statuses": [
          "active",
          "archived"
        ]
      },
      {
        "key": "word-practice",
        "label": "Kata kilat",
        "tool": "word-practice",
        "fields": [],
        "statuses": []
      },
      {
        "key": "reports",
        "label": "Laporan",
        "tool": "reports",
        "fields": [],
        "statuses": []
      }
    ],
    "id": "daily-apps",
    "name": "DailyOS",
    "purpose": "Satu workspace pribadi untuk perencanaan, kebiasaan, dokumen dan alat kerja sehari-hari.",
    "sources": [
      "daily-apps",
      "habitflow",
      "habitgrid",
      "routineflow",
      "hearth-os",
      "tripforge"
    ],
    "workflow": "Daftar → simpan kode pemulihan → buat workspace → rencanakan hari → check-in/tugas → laporan progres. Dokumen dan hasil tool dapat disimpan sebagai bagian workspace."
  }
};
