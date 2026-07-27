"""Type definitions untuk Pembersih File Duplikat."""
from dataclasses import dataclass
from typing import Optional, Set


@dataclass
class ScanOptions:
    """Opsi untuk scan folder."""
    folder: str
    exclude: Optional[Set[str]] = None
    min_size: int = 1024
    chunk_size: int = 65536
    hapus: bool = False
    kering: bool = False
    json_output: bool = False
    format_output: str = "text"


# Format output yang didukung
ALLOWED_FORMATS = ("text", "json")
