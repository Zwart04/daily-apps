"""
Shared type aliases and dataclasses for the ctx package.

This module defines the core data structures used throughout ctx:
the extraction result, file entry, and configuration types.
"""

from __future__ import annotations

import dataclasses
from typing import Dict, List, Optional, Tuple


@dataclasses.dataclass(frozen=True)
class FileEntry:
    """Represents a single file discovered during scanning.

    Attributes:
        path: Absolute filesystem path to the file.
        rel_path: Relative path from the scanning root.
        size: File size in bytes (0 if inaccessible).
    """

    path: str
    rel_path: str
    size: int


@dataclasses.dataclass(frozen=True)
class FileContent:
    """Represents a file that was successfully read.

    Attributes:
        path: Relative path used as a label/header.
        content: Decoded text content of the file.
        size: File size in bytes.
        lines: Number of lines in the content.
        encoding: The encoding used to decode the file (e.g. 'utf-8').
    """

    path: str
    content: str
    size: int
    lines: int
    encoding: str


@dataclasses.dataclass(frozen=True)
class TokenCount:
    """Detailed token count for extracted content.

    Attributes:
        total: Estimated or exact number of tokens.
        by_model: If exact tokenization was available, per-model breakdown.
        method: How the count was obtained ('exact' or 'estimated').
        characters: Total character count.
        words: Total word count (whitespace-split).
        lines: Total line count across all files.
    """

    total: int
    by_model: Dict[str, int] = dataclasses.field(default_factory=dict)
    method: str = "estimated"
    characters: int = 0
    words: int = 0
    lines: int = 0


@dataclasses.dataclass(frozen=True)
class ExtractResult:
    """The final output of a ctx extraction.

    Attributes:
        content: The formatted text content (markdown, plain, or json).
        files: List of FileContent entries that were read.
        tokens: TokenCount summary.
        format: The output format used ('markdown', 'plain', 'json').
        tree: Optional textual tree representation of scanned structure.
    """

    content: str
    files: List[FileContent]
    tokens: TokenCount
    format: str
    tree: str


# Supported output formats
OutputFormat = str  # Literal: 'markdown', 'plain', 'json'
ALLOWED_FORMATS: Tuple[str, ...] = ("markdown", "plain", "json")

# A collection of gitignore-style patterns
PatternList = List[str]

# Scanner options passed down from CLI / config
@dataclasses.dataclass(frozen=True)
class ScanOptions:
    """Options that control the scanning behaviour.

    Attributes:
        include: Glob patterns to include (empty = all).
        exclude: Glob patterns to exclude.
        max_depth: Maximum directory recursion depth.
        no_ignore: If True, ignore .gitignore rules.
        max_file_size: Maximum file size in bytes to read.
    """

    include: PatternList = dataclasses.field(default_factory=list)
    exclude: PatternList = dataclasses.field(default_factory=list)
    max_depth: int = 5
    no_ignore: bool = False
    max_file_size: int = 1_048_576  # 1 MB


# Default skip patterns (canonical from the functional spec)
DEFAULT_SKIP_PATTERNS: Tuple[str, ...] = (
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".env",
    "*.pyc",
    "*.egg-info",
    ".DS_Store",
)
