"""
File-tree scanner for ctx.

Walks a directory tree while respecting:
- .gitignore rules (via `GitignoreFilter`)
- Maximum recursion depth
- Include/exclude pattern filters

Outputs a list of `FileEntry` objects ready for reading.
"""

from __future__ import annotations

import os
import sys
from typing import List, Optional, Set

from .filters import FileFilter
from .types import DEFAULT_SKIP_PATTERNS, FileEntry, ScanOptions


def _count_depth(rel_path: str) -> int:
    """Count the number of directory separators in a relative path."""
    if not rel_path:
        return 0
    return rel_path.count(os.sep) + rel_path.count("/")


def scan_tree(root: str, options: ScanOptions) -> List[FileEntry]:
    """Walk *root* and return a filtered, depth-limited list of files.

    Args:
        root: Directory to scan.  Can be absolute or relative; will be
            resolved to an absolute path.
        options: ScanOptions controlling include/exclude/no_ignore/
            max_depth.

    Returns:
        A list of ``FileEntry`` objects for files that pass all filters.

    Raises:
        FileNotFoundError: If *root* does not exist.
        NotADirectoryError: If *root* is not a directory.
    """
    root = os.path.abspath(root)
    if not os.path.exists(root):
        raise FileNotFoundError(f"path does not exist: {root}")
    if not os.path.isdir(root):
        raise NotADirectoryError(f"path is not a directory: {root}")

    # Workaround: os.scandir with bytes on Linux returns bytes paths.
    file_filter = FileFilter(options, root)
    entries: List[FileEntry] = []

    # Use a stack for iterative directory traversal (avoids deep recursion)
    # Stack entries: (absolute_dir_path, relative_dir_path)
    stack: List[str] = [root]

    # Map: absolute path -> relative path
    # For root, rel = ""
    rel_base = root

    while stack:
        current_abs = stack.pop()
        current_rel = _rel_to_root(current_abs, root)

        depth = _count_depth(current_rel)
        if depth > options.max_depth:
            continue

        try:
            with os.scandir(current_abs) as it:
                for entry in it:
                    rel_path = entry.name if not current_rel else os.path.join(current_rel, entry.name)

                    # Check depth for directories before adding to stack
                    if entry.is_dir(follow_symlinks=False):
                        # Skip hidden git directories early for perf
                        if entry.name == ".git" and ".git" in DEFAULT_SKIP_PATTERNS:
                            continue
                        # Check filter for directories too, so we skip early
                        if not file_filter.accept(rel_path + "/"):
                            continue
                        dir_depth = _count_depth(rel_path)
                        if dir_depth <= options.max_depth:
                            stack.append(entry.path)
                        continue

                    if entry.is_file(follow_symlinks=False):
                        # Check filters
                        if not file_filter.accept(rel_path):
                            continue
                        try:
                            st = entry.stat(follow_symlinks=False)
                            size = st.st_size
                        except OSError:
                            size = 0

                        entries.append(
                            FileEntry(
                                path=entry.path,
                                rel_path=rel_path,
                                size=size,
                            )
                        )
        except PermissionError:
            print(f"ctx: warning: permission denied: {current_abs}", file=sys.stderr)
            continue
        except OSError as exc:
            print(f"ctx: warning: error scanning {current_abs}: {exc}", file=sys.stderr)
            continue

    # Sort for deterministic output
    entries.sort(key=lambda e: e.rel_path)
    return entries


def _rel_to_root(abs_path: str, root: str) -> str:
    """Return the path of *abs_path* relative to *root*.

    If *abs_path* equals *root*, returns an empty string.
    """
    if abs_path == root:
        return ""
    rel = os.path.relpath(abs_path, root)
    if rel.startswith(".."):
        # Should not happen with proper traversal, but be safe
        return ""
    return rel


def build_tree_string(
    entries: List[FileEntry],
    root: str,
    prefix: str = "",
    _dirs_visited: Optional[set] = None,
) -> str:
    """Build a human-readable tree representation of the scanned files.

    Args:
        entries: The file entries to display.
        root: The root directory for the tree.
        prefix: Internal use for indentation.
        _dirs_visited: Internal recursion set.

    Returns:
        A multi-line string resembling the ``tree`` command output.
    """
    if _dirs_visited is None:
        _dirs_visited = set()

    lines: List[str] = []
    root_name = os.path.basename(root.rstrip(os.sep)) or root

    # Build a hierarchical dict
    tree: dict = {}
    for e in entries:
        parts = e.rel_path.split(os.sep)
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        # Leaf files are stored as None
        node[parts[-1]] = None

    def _walk(node, depth, parent_prefix, is_last_list):
        items = sorted(node.items())
        for idx, (name, subtree) in enumerate(items):
            is_last = idx == len(items) - 1
            connector = "└── " if is_last else "├── "
            line = parent_prefix + connector + name
            lines.append(line)
            if subtree is not None:
                child_prefix = parent_prefix + ("    " if is_last else "│   ")
                _walk(subtree, depth + 1, child_prefix, is_last)

    lines.append(f"{root_name}/")
    _walk(tree, 0, "", True)
    return "\n".join(lines)
