"""Bulk git operations — pull, fetch, gc across multiple repos."""

import subprocess
import os
import sys
from dataclasses import dataclass, field
from .scanner import RepoInfo


@dataclass
class OpResult:
    """Result of a single operation on one repo."""

    repo: RepoInfo
    success: bool
    operation: str
    message: str = ""
    output: str = ""


def _run_git(cwd: str, *args: str, timeout: int = 60) -> tuple[int, str, str]:
    """Run git command in a specific directory."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except FileNotFoundError:
        return -2, "", "git not found"
    except OSError as e:
        return -3, "", str(e)


def _format_output(stdout: str, stderr: str, max_lines: int = 8) -> str:
    """Format stdout/stderr into a single readable string."""
    lines = []
    if stdout:
        for line in stdout.split("\n")[:max_lines]:
            lines.append(f"  {line}")
        if len(stdout.split("\n")) > max_lines:
            lines.append(f"  ... ({len(stdout.split('\n'))} total lines)")
    if stderr:
        lines.append(f"  stderr: {stderr[:300]}")
    return "\n".join(lines) if lines else "(no output)"


def pull_repos(repos: list[RepoInfo], strategy: str = "ff-only",
               timeout: int = 60, dry_run: bool = False) -> list[OpResult]:
    """Pull all repos.

    Args:
        repos: List of repos to pull.
        strategy: Merge strategy ('ff-only', 'rebase', 'merge', 'no-ff').
        timeout: Per-repo timeout in seconds.
        dry_run: If True, simulate without running.

    Returns:
        List of OpResult.
    """
    results: list[OpResult] = []
    for repo in repos:
        if not _can_operate(repo):
            results.append(OpResult(
                repo=repo, success=False, operation="pull",
                message=f"Skipped: {repo.error or 'invalid repo'}"
            ))
            continue

        if dry_run:
            results.append(OpResult(
                repo=repo, success=True, operation="pull",
                message=f"DRY-RUN: would pull {repo.branch or 'current branch'}"
            ))
            continue

        # Stash if dirty
        stashed = False
        if repo.is_dirty:
            rc, _, _ = _run_git(repo.path, "stash", "push", "-m", "gittree-auto-stash", timeout=timeout)
            if rc == 0:
                stashed = True
            else:
                results.append(OpResult(
                    repo=repo, success=False, operation="pull",
                    message="Dirty working tree and stash failed — skipping pull"
                ))
                continue

        args = ["pull"]
        if strategy == "ff-only":
            args.append("--ff-only")
        elif strategy == "rebase":
            args.append("--rebase")
        elif strategy == "no-ff":
            args.append("--no-ff")

        rc, stdout, stderr = _run_git(repo.path, *args, timeout=timeout)

        # Pop stash if we stashed
        if stashed:
            _run_git(repo.path, "stash", "pop", timeout=timeout)

        if rc == 0:
            results.append(OpResult(
                repo=repo, success=True, operation="pull",
                message="Pulled successfully",
                output=_format_output(stdout, stderr)
            ))
        else:
            error_msg = stderr[:200] if stderr else stdout[:200]
            results.append(OpResult(
                repo=repo, success=False, operation="pull",
                message=f"Pull failed: {error_msg}",
                output=_format_output(stdout, stderr)
            ))

    return results


def fetch_repos(repos: list[RepoInfo], timeout: int = 60,
                dry_run: bool = False) -> list[OpResult]:
    """Fetch all repos (non-destructive)."""
    results: list[OpResult] = []
    for repo in repos:
        if not _can_operate(repo):
            results.append(OpResult(
                repo=repo, success=False, operation="fetch",
                message=f"Skipped: {repo.error or 'invalid repo'}"
            ))
            continue

        if dry_run:
            results.append(OpResult(
                repo=repo, success=True, operation="fetch",
                message="DRY-RUN: would git fetch"
            ))
            continue

        rc, stdout, stderr = _run_git(repo.path, "fetch", "--all", "--prune", timeout=timeout)
        if rc == 0:
            results.append(OpResult(
                repo=repo, success=True, operation="fetch",
                message="Fetched all remotes",
                output=_format_output(stdout, stderr)
            ))
        else:
            results.append(OpResult(
                repo=repo, success=False, operation="fetch",
                message=f"Fetch failed: {(stderr or stdout)[:200]}"
            ))

    return results


def gc_repos(repos: list[RepoInfo], aggressive: bool = False,
             timeout: int = 120, dry_run: bool = False) -> list[OpResult]:
    """Run git gc on all repos."""
    results: list[OpResult] = []
    for repo in repos:
        if not _can_operate(repo):
            results.append(OpResult(
                repo=repo, success=False, operation="gc",
                message=f"Skipped: {repo.error or 'invalid repo'}"
            ))
            continue

        if dry_run:
            results.append(OpResult(
                repo=repo, success=True, operation="gc",
                message="DRY-RUN: would git gc"
            ))
            continue

        args = ["gc"]
        if aggressive:
            args.append("--aggressive")

        rc, stdout, stderr = _run_git(repo.path, *args, timeout=timeout)
        if rc == 0:
            results.append(OpResult(
                repo=repo, success=True, operation="gc",
                message="GC completed",
                output=_format_output(stdout, stderr)
            ))
        else:
            results.append(OpResult(
                repo=repo, success=False, operation="gc",
                message=f"GC failed: {(stderr or stdout)[:200]}"
            ))

    return results


def _can_operate(repo: RepoInfo) -> bool:
    """Check if we can run git operations on this repo."""
    if repo.error:
        return False
    if not os.path.isdir(repo.path):
        return False
    if not os.path.exists(os.path.join(repo.path, ".git")):
        return False
    return True
