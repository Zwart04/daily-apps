"""
ctx — Codebase Context Extractor for AI coding assistants.

Extract and format your codebase context for use with Claude, ChatGPT,
Copilot, and other AI coding tools. Zero external dependencies.

Usage:
    python3 -m ctx .                          # extract current directory
    python3 -m ctx src/ --format json         # extract src/ as JSON
    python3 -m ctx --include "*.py"           # only Python files
    python3 -m ctx . | pbcopy                 # copy to clipboard (macOS)
"""

from __future__ import annotations

from .types import ExtractResult, FileContent, FileEntry, TokenCount
from .scanner import scan_tree
from .reader import read_files
from .formatter import format_markdown, format_plain, format_json
from .counter import count_tokens


def extract(
    path: str = ".",
    *,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    max_depth: int = 5,
    max_file_size: int = 1_048_576,
    no_ignore: bool = False,
    format: str = "markdown",
    show_tree: bool = True,
) -> ExtractResult:
    """Extract codebase context from *path*.

    This is the main public API.  It scans, reads, and formats the
    codebase in one call.

    Args:
        path: Root directory to scan.
        include: Glob patterns to include (empty = all).
        exclude: Glob patterns to exclude (defaults skip .git, node_modules, etc.).
        max_depth: Maximum directory recursion depth.
        max_file_size: Maximum file size in bytes to read.
        no_ignore: If True, ignore .gitignore rules.
        format: Output format — ``"markdown"``, ``"plain"``, or ``"json"``.
        show_tree: Include a directory tree in the output.

    Returns:
        An ``ExtractResult`` with the formatted content and metadata.
    """
    from .config import load_config
    from .scanner import build_tree_string

    opts = load_config(
        path,
        overrides={
            "include": include or [],
            "exclude": exclude or [],
            "max_depth": max_depth,
            "no_ignore": no_ignore,
            "max_file_size": max_file_size,
        },
    )

    entries = scan_tree(path, opts)
    files = read_files(entries, opts.max_file_size)
    tree_str = build_tree_string(entries, path) if show_tree else ""

    formatters = {"markdown": format_markdown, "plain": format_plain, "json": format_json}
    fmt = formatters.get(format, format_markdown)
    content = fmt(files, tree=tree_str)
    tokens = count_tokens(content, files)

    return ExtractResult(
        content=content,
        files=files,
        tokens=tokens,
        format=format,
        tree=tree_str,
    )
