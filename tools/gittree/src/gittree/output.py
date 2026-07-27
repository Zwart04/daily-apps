"""Output formatting — plain, colored terminal, JSON, table."""

import json
import sys
from .scanner import RepoInfo
from .operations import OpResult

# ANSI color codes — hardcoded for zero-dependency
_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_RED = "\033[91m"
_GREEN = "\033[92m"
_YELLOW = "\033[93m"
_BLUE = "\033[94m"
_CYAN = "\033[96m"
_GRAY = "\033[90m"


def _status_icon(repo: RepoInfo) -> tuple[str, str]:
    """Return (icon, color_code) for a repo's status."""
    if repo.error:
        return "✗", _RED

    if repo.is_dirty:
        return "●", _YELLOW

    if repo.ahead > 0:
        return "↑", _CYAN

    if repo.behind > 0:
        return "↓", _YELLOW

    if repo.has_remote:
        return "✓", _GREEN

    return "○", _GRAY


def _format_path(rel_path: str, name: str, use_color: bool) -> str:
    """Format the repo path for display."""
    if rel_path == "." or not rel_path:
        return name
    return f"{rel_path}"


def print_status(repos: list[RepoInfo], use_color: bool = True,
                 output_format: str = "auto") -> None:
    """Print status of all repos."""
    if output_format == "json":
        print_status_json(repos)
        return

    if not repos:
        print("No git repositories found.")
        return

    # Header
    if use_color:
        print(f"{_DIM}Repositories found:{_RESET}")
    else:
        print("Repositories found:")

    # Sort: by path
    sorted_repos = sorted(repos, key=lambda r: r.relative_path)

    # Column widths
    max_path_len = max((len(r.relative_path or r.name) for r in sorted_repos), default=0)
    max_path_len = min(max_path_len + 1, 60)  # cap

    for repo in sorted_repos:
        icon, color = _status_icon(repo)
        path_str = _format_path(repo.relative_path, repo.name, use_color)
        padded_path = path_str.ljust(max_path_len)

        branch = repo.branch or "?"

        if repo.error:
            status = f"ERROR: {repo.error[:50]}"
            if use_color:
                print(f"  {color}{icon}{_RESET} {padded_path} {_DIM}{branch}{_RESET}  {color}{status}{_RESET}")
            else:
                print(f"  {icon} {padded_path} {branch}  {status}")
            continue

        # Build status tags
        tags = []
        if repo.is_dirty:
            parts = []
            if repo.staged > 0:
                parts.append(f"+{repo.staged}")
            if repo.unstaged > 0:
                parts.append(f"~{repo.unstaged}")
            if repo.untracked > 0:
                parts.append(f"?{repo.untracked}")
            tags.append(f"dirty({','.join(parts)})" if parts else "dirty")
        if repo.ahead > 0:
            tags.append(f"ahead {repo.ahead}")
        if repo.behind > 0:
            tags.append(f"behind {repo.behind}")
        if not repo.has_remote:
            tags.append("no-remote")

        status_str = "  ".join(tags) if tags else ""
        last_commit = repo.last_commit[:50] if repo.last_commit else ""

        if use_color:
            if repo.is_dirty:
                branch_color = _YELLOW
            elif repo.ahead > 0:
                branch_color = _CYAN
            elif repo.behind > 0:
                branch_color = _YELLOW
            else:
                branch_color = _GREEN

            print(f"  {color}{icon}{_RESET} {padded_path} {branch_color}{branch}{_RESET}", end="")
            if status_str:
                print(f"  {_YELLOW}{status_str}{_RESET}", end="")
            if last_commit:
                print(f"  {_DIM}{last_commit}{_RESET}", end="")
            print()
        else:
            print(f"  {icon} {padded_path} {branch}  {status_str}  {last_commit}".rstrip())

    # Summary line
    total = len(repos)
    clean = sum(1 for r in repos if not r.error and not r.is_dirty and r.ahead == 0)
    dirty = sum(1 for r in repos if r.is_dirty)
    unpushed = sum(1 for r in repos if r.ahead > 0 and not r.is_dirty)
    ahead = sum(1 for r in repos if r.ahead > 0)
    errors = sum(1 for r in repos if r.error)

    summary_parts = [f"{total} repos"]
    if use_color:
        summary_parts.append(f"{_GREEN}{clean} clean{_RESET}")
        if dirty:
            summary_parts.append(f"{_YELLOW}{dirty} dirty{_RESET}")
        if ahead:
            summary_parts.append(f"{_CYAN}{ahead} ahead{_RESET}")
        if errors:
            summary_parts.append(f"{_RED}{errors} errors{_RESET}")
    else:
        summary_parts.append(f"{clean} clean")
        if dirty:
            summary_parts.append(f"{dirty} dirty")
        if ahead:
            summary_parts.append(f"{ahead} ahead")
        if errors:
            summary_parts.append(f"{errors} errors")

    print()
    print("  " + ", ".join(summary_parts))


def print_status_json(repos: list[RepoInfo]) -> None:
    """Print repos as JSON."""
    data = []
    for r in repos:
        data.append({
            "path": r.path,
            "name": r.name,
            "relative_path": r.relative_path,
            "error": r.error,
            "branch": r.branch,
            "remote_url": r.remote_url,
            "has_remote": r.has_remote,
            "is_dirty": r.is_dirty,
            "staged": r.staged,
            "unstaged": r.unstaged,
            "untracked": r.untracked,
            "ahead": r.ahead,
            "behind": r.behind,
            "last_commit": r.last_commit,
            "last_commit_date": r.last_commit_date,
        })

    summary = {
        "total": len(repos),
        "clean": sum(1 for r in repos if not r.error and not r.is_dirty and r.ahead == 0),
        "dirty": sum(1 for r in repos if r.is_dirty),
        "ahead": sum(1 for r in repos if r.ahead > 0),
        "errors": sum(1 for r in repos if r.error),
    }

    output = {"repos": data, "summary": summary}
    print(json.dumps(output, indent=2))


def print_operations(results: list[OpResult], use_color: bool = True) -> None:
    """Print operation results."""
    success_count = sum(1 for r in results if r.success)
    fail_count = sum(1 for r in results if not r.success)

    for result in results:
        icon = "✓" if result.success else "✗"
        color = _GREEN if result.success else _RED

        if use_color:
            print(f"  {color}{icon}{_RESET} {result.repo.relative_path or result.repo.name}: {result.message}")
        else:
            print(f"  {icon} {result.repo.relative_path or result.repo.name}: {result.message}")

        if result.output:
            if use_color:
                print(f"    {_DIM}{result.output}{_RESET}")
            else:
                print(f"    {result.output}")

    # Summary
    total = len(results)
    if use_color:
        print()
        print(f"  {_GREEN}{success_count} succeeded{_RESET}", end="")
        if fail_count > 0:
            print(f", {_RED}{fail_count} failed{_RESET}", end="")
        print(f" — {total} total")
    else:
        print(f"\n  {success_count} succeeded, {fail_count} failed — {total} total")


def print_summary(repos: list[RepoInfo]) -> None:
    """Print a compact one-line summary."""
    total = len(repos)
    clean = sum(1 for r in repos if not r.error and not r.is_dirty and r.ahead == 0)
    dirty = sum(1 for r in repos if r.is_dirty)
    ahead = sum(1 for r in repos if r.ahead > 0)
    errors = sum(1 for r in repos if r.error)
    print(f"{total} repos — {clean} clean, {dirty} dirty, {ahead} ahead, {errors} errors")


def print_error(msg: str) -> None:
    """Print error message to stderr."""
    print(f"Error: {msg}", file=sys.stderr)
