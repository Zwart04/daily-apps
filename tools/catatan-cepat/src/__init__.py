"""Catatan Cepat — Catat apapun dari terminal dengan cepat.

Cara pakai:
    python3 -m src catat "Belanja: telur, susu, roti"
    python3 -m src lihat
    python3 -m src cari "belanja"
    python3 -m src --test
"""

from .cli import main
from .core import NoteManager
