"""Penyimpanan catatan — simpan dan baca catatan dari folder."""
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

from .types import FilterOptions, Note


class NoteStore:
    """Mengelola penyimpanan catatan di folder ~/.catatan-cepat/."""

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or os.path.expanduser("~/.catatan-cepat")
        self.notes_file = os.path.join(self.data_dir, "catatan.json")
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        """Buat folder penyimpanan jika belum ada."""
        os.makedirs(self.data_dir, exist_ok=True)

    def _baca_semua(self) -> Dict[str, Note]:
        """Baca semua catatan dari file JSON."""
        if not os.path.isfile(self.notes_file):
            return {}
        try:
            with open(self.notes_file, "r") as f:
                data = json.load(f)
            return {
                nid: Note(
                    id=nid,
                    judul=n["judul"],
                    isi=n["isi"],
                    tag=n.get("tag", ""),
                    dibuat=n["dibuat"],
                    diubah=n.get("diubah", n["dibuat"]),
                )
                for nid, n in data.items()
            }
        except (json.JSONDecodeError, KeyError, ValueError):
            return {}

    def _simpan_semua(self, notes: Dict[str, Note]) -> None:
        """Simpan semua catatan ke file JSON."""
        data = {
            nid: {
                "judul": n.judul,
                "isi": n.isi,
                "tag": n.tag,
                "dibuat": n.dibuat,
                "diubah": n.diubah,
            }
            for nid, n in notes.items()
        }
        with open(self.notes_file, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _buat_id(self) -> str:
        """Buat ID unik untuk catatan baru."""
        now = datetime.now()
        return now.strftime("%Y%m%d%H%M%S%f")[:-3]

    def tambah(self, judul: str, isi: str, tag: str = "") -> Note:
        """Tambah catatan baru.

        Args:
            judul: Judul catatan (baris pertama)
            isi: Isi catatan
            tag: Tag untuk mengelompokkan (opsional)

        Returns:
            Note yang baru dibuat
        """
        notes = self._baca_semua()
        now = datetime.now().isoformat()
        note_id = self._buat_id()
        note = Note(
            id=note_id,
            judul=judul,
            isi=isi,
            tag=tag.strip(),
            dibuat=now,
            diubah=now,
        )
        notes[note_id] = note
        self._simpan_semua(notes)
        return note

    def hapus(self, note_id: str) -> bool:
        """Hapus catatan berdasarkan ID.

        Returns:
            True jika berhasil, False jika ID tidak ditemukan
        """
        notes = self._baca_semua()
        if note_id not in notes:
            return False
        del notes[note_id]
        self._simpan_semua(notes)
        return True

    def cari(self, filter_opts: FilterOptions) -> List[Note]:
        """Cari catatan berdasarkan filter.

        Args:
            filter_opts: Filter yang digunakan

        Returns:
            Daftar catatan yang cocok
        """
        semua = self._baca_semua()
        hasil = list(semua.values())

        # Filter kata kunci
        if filter_opts.kata_kunci:
            keyword = filter_opts.kata_kunci.lower()
            hasil = [
                n for n in hasil
                if keyword in n.judul.lower()
                or keyword in n.isi.lower()
                or keyword in n.tag.lower()
            ]

        # Filter tag
        if filter_opts.tag:
            tag = filter_opts.tag.lower()
            hasil = [n for n in hasil if tag in n.tag.lower()]

        # Urutkan
        if filter_opts.urut == "terbaru":
            hasil.sort(key=lambda n: n.dibuat, reverse=True)
        else:
            hasil.sort(key=lambda n: n.dibuat)

        # Batasi jumlah
        return hasil[:filter_opts.batas]

    def dapatkan(self, note_id: str) -> Optional[Note]:
        """Ambil satu catatan berdasarkan ID."""
        notes = self._baca_semua()
        return notes.get(note_id)

    def semua_tag(self) -> List[str]:
        """Dapatkan daftar semua tag yang pernah dipakai."""
        notes = self._baca_semua().values()
        tags: set = set()
        for n in notes:
            if n.tag:
                for t in n.tag.split(","):
                    tags.add(t.strip())
        return sorted(tags)

    @property
    def total_catatan(self) -> int:
        """Jumlah total catatan."""
        return len(self._baca_semua())
