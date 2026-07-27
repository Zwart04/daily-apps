"""Config loader untuk Pembersih File Duplikat."""
import os
from typing import Dict

# Default config
DEFAULT_EXCLUDE_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".cache", "cache", "tmp", "temp", ".trash", "Trash",
    ".trash-1000", "$RECYCLE.BIN", "System Volume Information",
    "lost+found", "Thumbs.db", ".DS_Store",
}

DEFAULT_MIN_SIZE = 1024  # 1 KB — abaikan file lebih kecil dari ini


def load_config() -> Dict:
    """Load config dari environment variable, fallback ke default."""
    exclude_raw = os.environ.get("PDF_EXCLUDE_DIRS", "")
    exclude_dirs = DEFAULT_EXCLUDE_DIRS.copy()
    if exclude_raw:
        for d in exclude_raw.split(","):
            d = d.strip()
            if d:
                exclude_dirs.add(d)

    min_size_str = os.environ.get("PDF_MIN_SIZE", str(DEFAULT_MIN_SIZE))
    try:
        min_size = int(min_size_str)
    except ValueError:
        min_size = DEFAULT_MIN_SIZE

    return {
        "exclude_dirs": exclude_dirs,
        "min_size": min_size,
        "chunk_size": int(os.environ.get("PDF_CHUNK_SIZE", "65536")),  # 64KB per baca
    }
