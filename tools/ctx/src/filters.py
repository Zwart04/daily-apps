"""
Gitignore-aware include/exclude pattern filters for ctx.

Provides `GitignoreFilter` that understands gitignore-style wildcard
patterns and a `FileFilter` that combines the standard include/exclude
semantics.
"""

from __future__ import annotations

import fnmatch
import os
import re
import sys
from pathlib import Path
from typing import Callable, List, Optional, Pattern, Set

from .types import DEFAULT_SKIP_PATTERNS, ScanOptions

# ---------------------------------------------------------------------------
# Gitignore parsing
# ---------------------------------------------------------------------------

_GITIGNORE_COMMENT_RE = re.compile(r"^\s*(#|$)")


def _translate_gitignore(pattern: str) -> Pattern[str]:
    """Convert a gitignore-style pattern to a regex.

    Supports:
    - Leading ``/`` anchors to root
    - Trailing ``/`` matches only directories
    - ``**`` matches zero or more directories
    - ``*`` matches anything except ``/``
    - ``?`` matches single char except ``/``
    - ``[abc]`` character classes
    - ``!`` negation (caller strips the prefix)
    """
    raw = pattern
    anchored = raw.startswith("/")
    dir_only = raw.endswith("/")

    if anchored:
        raw = raw[1:]
    if dir_only:
        raw = raw[:-1]

    # Escape regex specials except *, ?, [, ]
    parts: List[str] = []
    i = 0
    while i < len(raw):
        c = raw[i]
        if c == "*":
            if i + 1 < len(raw) and raw[i + 1] == "*":
                # ** -- match everything including slashes
                parts.append(".*")
                i += 2
                # consume any trailing /
                if i < len(raw) and raw[i] == "/":
                    i += 1
            else:
                # * -- match everything except /
                parts.append("[^/]*")
                i += 1
        elif c == "?":
            parts.append("[^/]")
            i += 1
        elif c == "[":
            # Find the closing bracket
            j = i + 1
            if j < len(raw) and raw[j] in ("!", "^"):
                j += 1
            if j < len(raw) and raw[j] == "]":
                j += 1
            while j < len(raw) and raw[j] != "]":
                j += 1
            parts.append(raw[i : j + 1])
            i = j + 1
        else:
            parts.append(re.escape(c))
            i += 1

    regex_str = "".join(parts)
    if not anchored:
        regex_str = "(.*/)?" + regex_str
    else:
        regex_str = "^" + regex_str

    if dir_only:
        regex_str += "(/.*)?$"
    else:
        regex_str += "$"

    # Make it relative-path aware
    return re.compile(regex_str)


class GitignoreFilter:
    """Reads and applies ``.gitignore`` rules from a project root.

    Args:
        root: Absolute path to the project root that contains
            ``.gitignore``.
    """

    def __init__(self, root: str) -> None:
        self._root = os.path.abspath(root)
        self._negatives: List[Pattern[str]] = []
        self._positives: List[Pattern[str]] = []
        self._loaded = False

    def load(self) -> None:
        """Load rules from ``.gitignore`` at *root*.

        Safe to call multiple times; only loads once.
        """
        if self._loaded:
            return
        self._loaded = True
        gitignore_path = os.path.join(self._root, ".gitignore")
        if not os.path.isfile(gitignore_path):
            return
        try:
            with open(gitignore_path, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    raw = line.rstrip("\n\r")
                    if _GITIGNORE_COMMENT_RE.match(raw):
                        continue
                    if not raw:
                        continue
                    negate = raw.startswith("!")
                    pattern = raw[1:] if negate else raw
                    if negate:
                        self._negatives.append(_translate_gitignore(pattern))
                    else:
                        self._positives.append(_translate_gitignore(pattern))
        except OSError as exc:
            print(f"ctx: warning: could not read .gitignore: {exc}", file=sys.stderr)

    def is_ignored(self, rel_path: str) -> bool:
        """Check whether *rel_path* (relative to root) is gitignored.

        Returns ``True`` if the path matches any positive gitignore rule
        and is not re-included by a later negation rule.
        """
        self.load()
        # Normalise path separators to forward-slash
        normalised = rel_path.replace(os.sep, "/")
        # Negation rules take priority; most specific last wins
        matched = False
        for pat in self._positives:
            if pat.search(normalised):
                matched = True
        for pat in self._negatives:
            if pat.search(normalised):
                matched = False
        return matched


# ---------------------------------------------------------------------------
# File filtering
# ---------------------------------------------------------------------------


def _pattern_to_callable(pattern: str) -> Callable[[str], bool]:
    """Convert a fnmatch/glob pattern to a matcher callable."""
    compiled = re.compile(fnmatch.translate(pattern))
    return lambda path: bool(compiled.search(path.replace(os.sep, "/")))


class FileFilter:
    """Combines include/exclude lists + gitignore awareness.

    Args:
        options: ScanOptions controlling include/exclude/no_ignore.
        root: Absolute path used to resolve relative paths for gitignore.
    """

    def __init__(self, options: ScanOptions, root: str) -> None:
        self._include_patterns = [_pattern_to_callable(p) for p in options.include]
        self._exclude_patterns = [_pattern_to_callable(p) for p in options.exclude]
        self._gitignore: Optional[GitignoreFilter] = None
        if not options.no_ignore:
            self._gitignore = GitignoreFilter(root)

    def accept(self, rel_path: str) -> bool:
        """Return ``True`` if *rel_path* should be included.

        A file is accepted when:
        - It passes the gitignore filter (if enabled).
        - It does NOT match any exclude pattern.
        - It matches include patterns OR there are no include patterns.
        """
        normalised = rel_path.replace(os.sep, "/")
        # Strip trailing slash for consistent matching (directories get / appended)
        stripped = normalised.rstrip("/")

        # Gitignore
        if self._gitignore is not None and self._gitignore.is_ignored(normalised):
            return False

        # Exclude patterns (these always win)
        for matcher in self._exclude_patterns:
            if matcher(normalised) or matcher(stripped):
                return False

        # Include patterns
        if self._include_patterns:
            for matcher in self._include_patterns:
                if matcher(normalised) or matcher(stripped):
                    return True
            return False

        return True
