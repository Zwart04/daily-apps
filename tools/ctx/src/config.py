"""
Configuration loader for ctx.

Reads configuration from three sources, in ascending priority order:
1. `.ctxrc` or `ctx.rc` in the project root (INI-like format)
2. Environment variables (`CTX_INCLUDE`, `CTX_EXCLUDE`, `CTX_MAX_DEPTH`)
3. CLI arguments (not handled here; they override everything after merge)

This module provides a single public function `load_config()` that returns
a `ScanOptions` instance with merged configuration.
"""

from __future__ import annotations

import os
import shlex
import sys
from pathlib import Path
from typing import List, Optional

from .types import DEFAULT_SKIP_PATTERNS, ScanOptions

# Environment variable names
ENV_INCLUDE = "CTX_INCLUDE"
ENV_EXCLUDE = "CTX_EXCLUDE"
ENV_MAX_DEPTH = "CTX_MAX_DEPTH"
ENV_MAX_FILE_SIZE = "CTX_MAX_FILE_SIZE"
ENV_NO_IGNORE = "CTX_NO_IGNORE"


def _find_rc_file(start_dir: str) -> Optional[str]:
    """Walk up from *start_dir* looking for a .ctxrc or ctx.rc file.

    Returns the path to the first found rc file, or *None* if none exists.
    """
    current = Path(start_dir).resolve()
    for parent in [current] + list(current.parents):
        for candidate in (parent / ".ctxrc", parent / "ctx.rc"):
            if candidate.is_file():
                return str(candidate)
        # Stop at filesystem root
        if parent.parent == parent:
            break
    return None


def _parse_rc_file(path: str) -> dict:
    """Parse a simple key=value rc file, returning a dict.

    Lines starting with ``#`` or ``;`` are comments.  Empty lines are
    ignored.  Values may be quoted with single or double quotes.
    """
    config: dict = {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                stripped = line.strip()
                if not stripped or stripped.startswith(("#", ";")):
                    continue
                if "=" not in stripped:
                    continue
                key, _, value = stripped.partition("=")
                key = key.strip().upper()
                value = value.strip()
                # Strip surrounding quotes
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                    value = value[1:-1]
                config[key] = value
    except OSError as exc:
        print(f"ctx: warning: could not read rc file {path}: {exc}", file=sys.stderr)
    return config


def _parse_env_list(value: Optional[str]) -> List[str]:
    """Parse a comma- or space-separated list from an env var string."""
    if not value:
        return []
    # shlex.split handles quoting and spaces
    parts = shlex.split(value)
    result: List[str] = []
    for part in parts:
        result.extend(p.strip() for p in part.split(",") if p.strip())
    return result


def load_config(project_dir: Optional[str] = None, overrides: Optional[dict] = None) -> ScanOptions:
    """Load and merge ctx configuration from all sources.

    Priority (lowest to highest):
      1. Built-in defaults
      2. RC file (``.ctxrc`` / ``ctx.rc``)
      3. Environment variables
      4. *overrides* dict (from CLI args)

    Args:
        project_dir: Root directory to search for RC files.  Uses CWD if
            *None*.
        overrides: Optional dict whose keys map to ``ScanOptions`` field
            names (e.g. ``max_depth``, ``include``, ``exclude``) to
            override everything else.

    Returns:
        A fully resolved ``ScanOptions`` instance.
    """
    if project_dir is None:
        project_dir = os.getcwd()

    # --- 1. Start with defaults ---
    include: List[str] = []
    exclude: List[str] = list(DEFAULT_SKIP_PATTERNS)
    max_depth: int = 5
    no_ignore: bool = False
    max_file_size: int = 1_048_576

    # --- 2. RC file ---
    rc_path = _find_rc_file(project_dir)
    if rc_path is not None:
        rc = _parse_rc_file(rc_path)
        if "INCLUDE" in rc:
            include = shlex.split(rc["INCLUDE"])
        if "EXCLUDE" in rc:
            exclude = shlex.split(rc["EXCLUDE"])
        if "MAX_DEPTH" in rc:
            try:
                max_depth = int(rc["MAX_DEPTH"])
            except ValueError:
                print(f"ctx: warning: invalid MAX_DEPTH in {rc_path}", file=sys.stderr)
        if "MAX_FILE_SIZE" in rc:
            try:
                max_file_size = int(rc["MAX_FILE_SIZE"])
            except ValueError:
                print(f"ctx: warning: invalid MAX_FILE_SIZE in {rc_path}", file=sys.stderr)
        if rc.get("NO_IGNORE", "").lower() in ("1", "true", "yes"):
            no_ignore = True

    # --- 3. Environment variables ---
    env_include = _parse_env_list(os.environ.get(ENV_INCLUDE))
    env_exclude = _parse_env_list(os.environ.get(ENV_EXCLUDE))
    env_max_depth = os.environ.get(ENV_MAX_DEPTH)
    env_max_file_size = os.environ.get(ENV_MAX_FILE_SIZE)
    env_no_ignore = os.environ.get(ENV_NO_IGNORE)

    if env_include:
        include = env_include
    if env_exclude:
        exclude = env_exclude
    if env_max_depth is not None:
        try:
            max_depth = int(env_max_depth)
        except ValueError:
            print(f"ctx: warning: invalid {ENV_MAX_DEPTH}", file=sys.stderr)
    if env_max_file_size is not None:
        try:
            max_file_size = int(env_max_file_size)
        except ValueError:
            print(f"ctx: warning: invalid {ENV_MAX_FILE_SIZE}", file=sys.stderr)
    if env_no_ignore is not None:
        no_ignore = env_no_ignore.lower() in ("1", "true", "yes")

    # --- 4. Overrides (from CLI) ---
    if overrides is not None:
        if "include" in overrides and overrides["include"] is not None:
            include = overrides["include"]
        if "exclude" in overrides and overrides["exclude"] is not None:
            exclude = overrides["exclude"]
        if "max_depth" in overrides and overrides["max_depth"] is not None:
            max_depth = overrides["max_depth"]
        if "no_ignore" in overrides:
            no_ignore = bool(overrides["no_ignore"])
        if "max_file_size" in overrides and overrides["max_file_size"] is not None:
            max_file_size = overrides["max_file_size"]

    # Validate
    if max_depth < 0:
        print("ctx: warning: max_depth must be >= 0, using 0", file=sys.stderr)
        max_depth = 0
    if max_file_size < 0:
        print("ctx: warning: max_file_size must be >= 0, using 0", file=sys.stderr)
        max_file_size = 0

    return ScanOptions(
        include=include,
        exclude=exclude,
        max_depth=max_depth,
        no_ignore=no_ignore,
        max_file_size=max_file_size,
    )
