"""Pemformat output untuk Catatan Cepat."""
from datetime import datetime
from typing import List

from .types import Note


def format_daftar(notes: List[Note]) -> str:
    """Format daftar catatan untuk ditampilkan."""
    if not notes:
        return "Belum ada catatan. Buat catatan baru dengan: python3 -m src catat \"judul\""

    lines = []
    lines.append("=" * 60)
    lines.append(f"  CATATAN ({len(notes)} ditemukan)")
    lines.append("=" * 60)
    lines.append("")

    for i, note in enumerate(notes, 1):
        # Format judul
        judul = note.judul[:60]
        if len(note.judul) > 60:
            judul += "..."

        # Format tanggal
        try:
            tgl = datetime.fromisoformat(note.dibuat)
            tgl_str = tgl.strftime("%d/%m/%Y %H:%M")
        except (ValueError, TypeError):
            tgl_str = note.dibuat[:16]

        # Tag
        tag_str = f" [{note.tag}]" if note.tag else ""

        # Baris
        lines.append(f"  [{i}] {judul}")
        lines.append(f"      ID: {note.id} | {tgl_str}{tag_str}")

        # Isi (potong ke 1 baris)
        isi_satu_baris = note.isi.replace("\n", " ")[:70]
        if isi_satu_baris != note.judul[:70]:
            lines.append(f"      {isi_satu_baris}")

        lines.append("")

    return "\n".join(lines)


def format_detail(note: Note) -> str:
    """Format detail satu catatan."""
    try:
        tgl = datetime.fromisoformat(note.dibuat)
        tgl_str = tgl.strftime("%d %B %Y %H:%M")
    except (ValueError, TypeError):
        tgl_str = note.dibuat

    try:
        ubah = datetime.fromisoformat(note.diubah)
        ubah_str = ubah.strftime("%d %B %Y %H:%M")
    except (ValueError, TypeError):
        ubah_str = note.diubah

    lines = []
    lines.append("=" * 60)
    lines.append(f"  {note.judul}")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"  ID        : {note.id}")
    if note.tag:
        lines.append(f"  Tag       : {note.tag}")
    lines.append(f"  Dibuat    : {tgl_str}")
    lines.append(f"  Diubah    : {ubah_str}")
    lines.append("")
    lines.append("-" * 60)
    lines.append("")
    lines.append(note.isi)
    lines.append("")
    lines.append("-" * 60)

    return "\n".join(lines)


def format_stats(stats: dict) -> str:
    """Format statistik."""
    lines = []
    lines.append("=" * 60)
    lines.append("  STATISTIK CATATAN")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"  Total catatan   : {stats['total']}")
    lines.append(f"  Total tag       : {stats['total_tag']}")
    if stats["tag_terpopuler"]:
        lines.append("")
        lines.append("  Tag terpopuler:")
        for t in stats["tag_terpopuler"]:
            lines.append(f"    - {t}")
    lines.append("")
    return "\n".join(lines)
