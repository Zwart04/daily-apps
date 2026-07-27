"""Directory scanner — find git repositories in a directory tree."""

import os
import stat
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class RepoInfo:
    """Information about a discovered git repository."""

    path: str
    name: str
    relative_path: str
    error: str | None = None
    branch: str | None = None
    remote_url: str | None = None
    is_dirty: bool = False
    staged: int = 0
    unstaged: int = 0
    untracked: int = 0
    ahead: int = 0
    behind: int = 0
    last_commit: str | None = None
    last_commit_date: str | None = None
    has_remote: bool = False


def _is_git_dir(path: str) -> bool:
    """Check if path contains a .git directory (or is a .git file for worktrees)."""
    git_path = os.path.join(path, ".git")
    return os.path.isdir(git_path) or os.path.isfile(git_path)


def _should_skip(entry_name: str, skip_set: set) -> bool:
    """Check if directory name is in the skip list."""
    if entry_name in skip_set:
        return True
    for pat in skip_set:
        if pat.startswith("*") and entry_name.endswith(pat[1:]):
            return True
        if pat.endswith("*") and entry_name.startswith(pat[:-1]):
            return True
    return False


def scan_repos(root_dir: str, max_depth: int = 3, skip_set: set | None = None) -> list[RepoInfo]:
    """Scan directory tree for git repositories up to max_depth.

    Args:
        root_dir: Root directory to scan.
        max_depth: Maximum directory depth to traverse (default: 3).
        skip_set: Set of directory names to skip.

    Returns:
        List of RepoInfo objects.
    """
    if skip_set is None:
        skip_set = {"node_modules", ".cache", "__pycache__", "venv", ".venv", ".git",
                     ".hg", ".svn", "build", "dist", "target", ".next", ".turbo",
                     ".svelte-kit", ".nx", "coverage", ".nyc_output", ".pytest_cache",
                     ".mypy_cache", ".ruff_cache", ".tox", ".eggs"}

    root_dir = os.path.abspath(root_dir)
    repos: list[RepoInfo] = []

    # Normalize root_dir — resolve symlinks to avoid duplicate scans
    try:
        root_dir = os.path.realpath(root_dir)
    except OSError:
        root_dir = os.path.abspath(root_dir)

    if not os.path.isdir(root_dir):
        return repos

    root_path = Path(root_dir)

    # Track visited realpaths to avoid following symlink cycles
    visited: set[str] = set()

    def _scan(current: Path, depth: int):
        if depth > max_depth:
            return

        try:
            real = os.path.realpath(str(current))
            if real in visited:
                return
            visited.add(real)
        except OSError:
            return

        try:
            entries = list(current.iterdir())
        except (PermissionError, OSError):
            return

        # Check if current directory is itself a git repo
        if _is_git_dir(str(current)):
            rel = ""
            try:
                rel = str(current.relative_to(root_path))
            except ValueError:
                rel = str(current)
            if rel == ".":
                name = os.path.basename(root_dir) or root_dir
            else:
                name = os.path.basename(str(current))
            repos.append(RepoInfo(
                path=str(current),
                name=name,
                relative_path=rel,
            ))
            # Don't recurse into a repo's subdirectories (they're tracked by git)
            return

        for entry in sorted(entries, key=lambda e: e.name):
            if not entry.is_dir() or entry.is_symlink():
                continue
            if entry.name.startswith(".") and entry.name != ".config":
                continue
            if _should_skip(entry.name, skip_set):
                continue
            _scan(entry, depth + 1)

    _scan(root_path, 0)
    return repos
