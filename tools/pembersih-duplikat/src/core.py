"""Core logic untuk mendeteksi file duplikat.

Strategi:
1. Scan folder rekursif, kumpulkan semua file
2. Kelompokkan berdasarkan ukuran file (byte)
3. Untuk file dengan ukuran sama, hitung hash SHA256 dari awal file (first_chunk)
4. Untuk file dengan hash awal sama, hitung hash SHA256 full file
5. Kelompokkan file dengan hash full yang sama => duplikat
"""
import hashlib
import os
from typing import Dict, List, Optional, Set, Tuple

from .config import load_config

ChunkResult = Tuple[str, int, str]  # (path, size, hash)


def _should_exclude(name: str, exclude_dirs: Set[str]) -> bool:
    """Cek apakah file/dir harus di-exclude."""
    for pattern in exclude_dirs:
        if pattern in name.split(os.sep):
            return True
    return False


def scan_folder(folder: str, exclude_dirs: Set[str], min_size: int) -> List[str]:
    """Scan folder rekursif, return daftar path file."""
    files: List[str] = []
    folder = os.path.abspath(folder)

    if not os.path.isdir(folder):
        raise FileNotFoundError(f"Folder tidak ditemukan: {folder}")

    for root, dirs, filenames in os.walk(folder, followlinks=False):
        # Filter direktori yang di-exclude (modify dirs in-place)
        dirs[:] = [d for d in dirs if not _should_exclude(d, exclude_dirs)]

        for fname in filenames:
            fpath = os.path.join(root, fname)
            try:
                st = os.stat(fpath, follow_symlinks=False)
                if st.st_size >= min_size:
                    files.append(fpath)
            except (OSError, PermissionError):
                continue

    return files


def _hash_file(fpath: str, chunk_size: int = 65536, full: bool = False,
               max_bytes: Optional[int] = None) -> Optional[str]:
    """Hitung SHA256 file. Jika full=False, hanya baca chunk pertama."""
    try:
        h = hashlib.sha256()
        with open(fpath, "rb") as f:
            if full:
                while True:
                    data = f.read(chunk_size)
                    if not data:
                        break
                    h.update(data)
            else:
                data = f.read(chunk_size)
                if data:
                    h.update(data)
        return h.hexdigest()
    except (OSError, PermissionError):
        return None


def group_by_size(files: List[str]) -> Dict[int, List[str]]:
    """Kelompokkan file berdasarkan ukuran."""
    groups: Dict[int, List[str]] = {}
    for fpath in files:
        try:
            size = os.path.getsize(fpath)
        except (OSError, PermissionError):
            continue
        if size not in groups:
            groups[size] = []
        groups[size].append(fpath)
    return groups


def filter_duplicates(groups: Dict[int, List[str]],
                      chunk_size: int = 65536) -> Dict[str, List[str]]:
    """Filter grup ukuran untuk cari duplikat sejati via hash."""
    # Phase 1: hash chunk pertama untuk eliminasi cepat
    candidates: Dict[str, List[str]] = {}
    for size, file_list in groups.items():
        if len(file_list) < 2:
            continue
        for fpath in file_list:
            h = _hash_file(fpath, chunk_size, full=False)
            if h is None:
                continue
            if h not in candidates:
                candidates[h] = []
            candidates[h].append(fpath)

    # Phase 2: hash full untuk konfirmasi
    duplicates: Dict[str, List[str]] = {}
    for chunk_hash, file_list in candidates.items():
        if len(file_list) < 2:
            continue

        full_hash_groups: Dict[str, List[str]] = {}
        for fpath in file_list:
            h = _hash_file(fpath, chunk_size, full=True)
            if h is None:
                continue
            if h not in full_hash_groups:
                full_hash_groups[h] = []
            full_hash_groups[h].append(fpath)

        for fh, fg in full_hash_groups.items():
            if len(fg) >= 2:
                duplicates[fh] = fg

    return duplicates


def hitung_ruang_terbuang(duplicates: Dict[str, List[str]]) -> int:
    """Hitung total byte yang terbuang karena duplikat."""
    total = 0
    seen: Set[int] = set()
    for fhash, flist in duplicates.items():
        # Simpan satu, hitung sisanya
        for i, fpath in enumerate(flist):
            if i == 0:
                continue
            try:
                size = os.path.getsize(fpath)
                if id(fpath) not in seen:
                    total += size
                    seen.add(id(fpath))
            except (OSError, PermissionError):
                continue
    return total


def cari_duplikat(folder: str, exclude_dirs: Optional[Set[str]] = None,
                  min_size: int = 1024, chunk_size: int = 65536,
                  progress_callback=None) -> Dict[str, List[str]]:
    """Cari file duplikat di folder. Return dict hash -> list path."""
    if exclude_dirs is None:
        cfg = load_config()
        exclude_dirs = cfg["exclude_dirs"]

    files = scan_folder(folder, exclude_dirs, min_size)
    if progress_callback:
        progress_callback(f"Scan selesai: {len(files)} file ditemukan")

    groups = group_by_size(files)
    if progress_callback:
        candidates = sum(1 for g in groups.values() if len(g) >= 2)
        progress_callback(f"Potensi duplikat: {candidates} grup ukuran")

    duplicates = filter_duplicates(groups, chunk_size)
    return duplicates
