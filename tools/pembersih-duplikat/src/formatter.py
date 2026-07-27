"""Formatters untuk output Pembersih File Duplikat."""
import os
import json
from typing import Dict, List


def _format_bytes(byte_count: int) -> str:
    """Format byte ke unit yang mudah dibaca."""
    for unit in ["B", "KB", "MB", "GB"]:
        if byte_count < 1024:
            return f"{byte_count:.1f} {unit}"
        byte_count /= 1024
    return f"{byte_count:.1f} TB"


def format_output(duplicates: Dict[str, List[str]],
                  fmt: str = "text") -> str:
    """Format hasil pencarian duplikat."""
    if fmt == "json":
        return json.dumps(duplicates, indent=2, ensure_ascii=False)

    if not duplicates:
        return "Tidak ditemukan file duplikat."

    lines: List[str] = []
    total_ruang = 0
    grup_count = 0

    for fhash, flist in duplicates.items():
        grup_count += 1
        # Ambil ukuran dari file pertama
        try:
            size = os.path.getsize(flist[0])
        except (OSError, PermissionError):
            size = 0
        ruang_grup = size * (len(flist) - 1)
        total_ruang += ruang_grup

        lines.append(f"\n=== Grup {grup_count} ({len(flist)} file, masing-masing {_format_bytes(size)}) ===")
        for i, fpath in enumerate(flist):
            label = "(asli)" if i == 0 else "(duplikat)"
            lines.append(f"  {label} {fpath}")

    lines.append(f"\n--- Ringkasan ---")
    lines.append(f"Total grup duplikat: {grup_count}")
    lines.append(f"Total file duplikat: {sum(len(v)-1 for v in duplicates.values())}")
    lines.append(f"Total ruang terbuang: {_format_bytes(total_ruang)}")

    return "\n".join(lines)
