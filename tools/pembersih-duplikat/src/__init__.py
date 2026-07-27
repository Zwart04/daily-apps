"""Pembersih File Duplikat — Cari dan bersihkan file duplikat di komputer.

Usage:
    python3 -m src <folder>
    python3 -m src <folder> --hapus
    python3 -m src <folder> --kering
    python3 -m src --test
"""
from .cli import main
from .core import cari_duplikat
