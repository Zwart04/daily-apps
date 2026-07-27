"""Tipe data untuk Catatan Cepat."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Note:
    """Satu catatan."""
    id: str
    judul: str
    isi: str
    tag: str
    dibuat: str  # ISO format timestamp
    diubah: str  # ISO format timestamp


@dataclass
class FilterOptions:
    """Filter untuk mencari catatan."""
    kata_kunci: Optional[str] = None
    tag: Optional[str] = None
    batas: int = 20
    urut: str = "terbaru"  # "terbaru" atau "terlama"
