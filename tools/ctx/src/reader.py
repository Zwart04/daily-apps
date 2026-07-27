"""
File content reader for ctx.

Handles reading text files with:
- Binary detection (magic bytes + heuristics)
- Graceful encoding fallback (utf-8 -> latin-1 -> binary-exception)
- File-size limits
- Per-file content metadata
"""

from __future__ import annotations

import os
import sys
from typing import List, Optional, Tuple

from .types import DEFAULT_SKIP_PATTERNS, FileContent, FileEntry


# Magic bytes that indicate binary content
# (first 4 bytes of common binary formats)
_BINARY_MAGIC_BYTES: List[bytes] = [
    b"\x00",  # Null byte (strong indicator of binary)
    b"\xff\xd8\xff",  # JPEG
    b"\x89PNG",  # PNG
    b"GIF8",  # GIF
    b"\x1f\x8b",  # gzip
    b"BZ",  # bzip2
    b"\xfd7zXZ",  # xz
    b"\x7fELF",  # ELF binary
    b"MZ",  # PE (Windows executable)
    b"\xca\xfe\xba\xbe",  # Java class
    b"%PDF",  # PDF — allow through since we have text extractors may handle
    # but we treat as binary because pdftotext not available
    b"PK",  # ZIP/DOCX/XLSX
    b"\x1f\x9d",  # compress
    b"\x1f\xa0",  # compress (LZH)
    b"\x04\x22\x4d\x18",  # LZ4
    b"\x28\xb5\x2f\xfd",  # Zstandard
]

# Extensions that are definitively text
_TEXT_EXTENSIONS: set = {
    ".py", ".pyw", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".java", ".kt", ".kts", ".scala", ".clj", ".cljs",
    ".c", ".h", ".cpp", ".hpp", ".cc", ".cxx", ".hxx", ".cs",
    ".go", ".rs", ".rb", ".php", ".pl", ".pm", ".t", ".swift",
    ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
    ".html", ".htm", ".xhtml", ".css", ".scss", ".sass", ".less",
    ".xml", ".svg", ".json", ".yaml", ".yml", ".toml", ".ini",
    ".cfg", ".conf", ".md", ".rst", ".txt", ".log",
    ".env", ".gitignore", ".gitattributes", ".editorconfig",
    ".npmrc", ".yarnrc", ".dockerfile", ".dockerignore",
    ".sql", ".r", ".m", ".mm", ".cmake", ".mk", ".makefile",
    ".lua", ".hs", ".ex", ".exs", ".erl", ".hrl",
    ".svelte", ".vue", ".astro", ".nim", ".zig",
    ".tf", ".tfvars", ".hcl",
    ".proto", ".gradle", ".groovy",
    ".kt", ".kts",
    ".cmake", ".cmake.in",
    "Makefile", "makefile", "GNUmakefile",
    "Dockerfile", "dockerfile",
    "Justfile", "justfile",
    ".applescript",
    ".tex", ".sty", ".cls", ".bib",
    ".nix",
    ".flake8", ".pylintrc",
    ".babelrc", ".eslintrc", ".prettierrc",
    ".liquid", ".erb", ".haml", ".slim",
    ".patch", ".diff",
}

# File names (without extension) that are plain text
_TEXT_FILENAMES: set = {
    "Makefile", "makefile", "GNUmakefile",
    "Dockerfile", "dockerfile",
    "Justfile", "justfile",
    "Procfile",
    "requirements.txt",
    "CHANGELOG", "CHANGES", "NEWS",
    "README", "LICENSE", "COPYING",
    "VERSION", "MANIFEST.in",
}


def _has_binary_magic(data: bytes) -> bool:
    """Check if *data* starts with a known binary magic byte sequence.

    Also returns ``True`` if a null byte appears in the first 8 KB
    (a strong heuristic).
    """
    # Check magic bytes
    for magic in _BINARY_MAGIC_BYTES:
        if data[: len(magic)] == magic:
            # PDF exception: only treat as binary if PDF
            if data[:4] == b"%PDF":
                return True
            return True

    # Null byte heuristic — scan first 8 KB
    chunk = data[:8192]
    if b"\x00" in chunk:
        return True

    return False


def _is_text_by_filename(rel_path: str) -> Optional[bool]:
    """Heuristic check based on file extension or name.

    Returns:
        ``True`` if definitely text,
        ``False`` if definitely binary,
        ``None`` if uncertain.
    """
    basename = os.path.basename(rel_path)
    ext = os.path.splitext(basename)[1].lower()

    if ext in _TEXT_EXTENSIONS:
        return True
    if basename in _TEXT_FILENAMES:
        return True

    # Known binary extensions
    _binary_exts = {
        ".o", ".obj", ".lib", ".a", ".so", ".dll", ".dylib",
        ".exe", ".bin", ".dat",
        ".zip", ".tar", ".gz", ".bz2", ".xz", ".zst",
        ".png", ".jpg", ".jpeg", ".gif", ".ico", ".bmp", ".webp",
        ".mp3", ".mp4", ".avi", ".mov", ".mkv", ".wav", ".flac",
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".ttf", ".otf", ".woff", ".woff2", ".eot",
        ".pyc", ".pyo", ".pyd",
        ".db", ".sqlite", ".sqlite3",
        ".class", ".jar",
        ".iso", ".img",
        ".pak", ".unity3d", ".blend",
        ".tfrecord", ".h5", ".hdf5", ".pb",
        ".whl", ".egg",
        ".DS_Store",
    }
    if ext in _binary_exts:
        return False

    return None


def read_file(entry: FileEntry, max_file_size: int = 1_048_576) -> Optional[FileContent]:
    """Read and decode a single file entry.

    The function applies multiple strategies:
    1. Check filename for binary/text hint.
    2. Read the first few bytes and check for binary magic.
    3. Try UTF-8; on failure fall back to latin-1.
    4. If both fail, return ``None`` (skip).

    Args:
        entry: File metadata from the scanner.
        max_file_size: Maximum bytes to read (files larger than this
            are skipped with a warning).

    Returns:
        A ``FileContent`` object on success, or ``None`` if the file
        should be skipped (binary, too large, or unreadable).
    """
    # Filename heuristic
    fn_hint = _is_text_by_filename(entry.rel_path)
    if fn_hint is False:
        return None

    # Check size
    if entry.size > max_file_size and max_file_size > 0:
        print(
            f"ctx: skipping {entry.rel_path} ({entry.size} bytes > {max_file_size} limit)",
            file=sys.stderr,
        )
        return None

    # Try to open
    try:
        with open(entry.path, "rb") as fh:
            # Check magic bytes from beginning
            header = fh.read(8192)
            if _has_binary_magic(header) and fn_hint is not True:
                return None

            # Read the whole file
            fh.seek(0)
            raw = fh.read()
    except OSError as exc:
        print(f"ctx: warning: could not read {entry.rel_path}: {exc}", file=sys.stderr)
        return None

    # Attempt decoding
    for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            text = raw.decode(enc)
            lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
            return FileContent(
                path=entry.rel_path,
                content=text,
                size=entry.size,
                lines=lines,
                encoding=enc,
            )
        except (UnicodeDecodeError, LookupError):
            continue

    # No encoding worked
    print(f"ctx: warning: could not decode {entry.rel_path} with any encoding", file=sys.stderr)
    return None


def read_files(
    entries: List[FileEntry],
    max_file_size: int = 1_048_576,
) -> List[FileContent]:
    """Read multiple file entries.

    Args:
        entries: List of file entries to read.
        max_file_size: Maximum allowed file size in bytes.

    Returns:
        A list of successfully read ``FileContent`` objects (skipped/
        binary files are omitted).
    """
    results: List[FileContent] = []
    for entry in entries:
        result = read_file(entry, max_file_size)
        if result is not None:
            results.append(result)
    return results
