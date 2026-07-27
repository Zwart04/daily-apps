"""Logika utama Catatan Cepat — import dan export."""
import json
import os
from datetime import datetime
from typing import List

from .store import NoteStore
from .types import FilterOptions, Note


class NoteManager:
    """Manager catatan — menghubungkan CLI dengan penyimpanan."""

    def __init__(self, store: NoteStore):
        self.store = store

    def catat(self, judul: str, isi: str = "", tag: str = "") -> Note:
        """Buat catatan baru."""
        return self.store.tambah(judul, isi if isi else judul, tag)

    def lihat_semua(self, filter_opts: FilterOptions) -> List[Note]:
        """Lihat semua catatan dengan filter."""
        return self.store.cari(filter_opts)

    def lihat_satu(self, note_id: str) -> Note:
        """Lihat detail satu catatan."""
        note = self.store.dapatkan(note_id)
        if not note:
            raise ValueError(f"Catatan dengan ID '{note_id}' tidak ditemukan")
        return note

    def hapus(self, note_id: str) -> bool:
        """Hapus catatan."""
        return self.store.hapus(note_id)

    def export_json(self, filepath: str, filter_opts: FilterOptions) -> str:
        """Export catatan ke file JSON.

        Args:
            filepath: Path file output
            filter_opts: Filter catatan

        Returns:
            Path file yang disimpan
        """
        notes = self.store.cari(filter_opts)
        data = [
            {
                "id": n.id,
                "judul": n.judul,
                "isi": n.isi,
                "tag": n.tag,
                "dibuat": n.dibuat,
                "diubah": n.diubah,
            }
            for n in notes
        ]
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filepath

    def export_markdown(self, filepath: str, filter_opts: FilterOptions) -> str:
        """Export catatan ke file Markdown.

        Args:
            filepath: Path file output
            filter_opts: Filter catatan

        Returns:
            Path file yang disimpan
        """
        notes = self.store.cari(filter_opts)
        lines = ["# Catatan Saya\n", f"Dibuat: {datetime.now().strftime('%d %B %Y %H:%M')}\n", "---\n"]
        for n in notes:
            lines.append(f"## {n.judul}\n")
            if n.tag:
                lines.append(f"Tag: {n.tag}\n")
            lines.append(f"_{n.dibuat}_\n")
            lines.append("")
            lines.append(n.isi)
            lines.append("")
            lines.append("---\n")

        with open(filepath, "w") as f:
            f.write("\n".join(lines))
        return filepath

    def stats(self) -> dict:
        """Dapatkan statistik catatan."""
        semua = self.lihat_semua(FilterOptions(batas=999999))
        return {
            "total": len(semua),
            "total_tag": len(self.store.semua_tag()),
            "tag_terpopuler": self._tag_populer(semua),
        }

    def _tag_populer(self, notes: List[Note]) -> List[str]:
        """Cari tag yang paling sering dipakai."""
        tag_count: dict = {}
        for n in notes:
            if n.tag:
                for t in n.tag.split(","):
                    t = t.strip()
                    if t:
                        tag_count[t] = tag_count.get(t, 0) + 1
        sorted_tags = sorted(tag_count.items(), key=lambda x: -x[1])
        return [f"{tag} ({count})" for tag, count in sorted_tags[:10]]
