#!/usr/bin/env python3
"""
gittree — Git Repository Tree Manager.

Scan directories, inspect status, and operate on multiple git repos in bulk.
Zero external dependencies.

Usage:
    gittree status [PATH]            Show status of all repos under PATH
    gittree pull [PATH]              Pull all repos
    gittree fetch [PATH]             Fetch all repos
    gittree gc [PATH]                Run git gc on all repos
    gittree dirty [PATH]             Only show repos with changes
    gittree summary [PATH]           Compact one-line summary
    gittree --test                   Run self-test
    gittree --help                   Show this help
"""

import argparse
import json
import os
import sys
import time

from . import __version__
from .config import load_config
from .scanner import scan_repos
from .status import enrich_all
from .operations import pull_repos, fetch_repos, gc_repos
from .output import (
    print_status,
    print_operations,
    print_summary,
    print_error,
    _RESET, _BOLD, _DIM, _GREEN, _CYAN, _YELLOW, _RED, _GRAY,
)


def _detect_color() -> bool:
    """Detect if terminal supports color."""
    if "NO_COLOR" in os.environ:
        return False
    if "GITTREE_COLOR" in os.environ:
        return os.environ["GITTREE_COLOR"].lower() in ("1", "true", "yes", "on")
    return sys.stdout.isatty()


def _resolve_path(path: str | None) -> str:
    """Resolve the scan path."""
    if path:
        return os.path.abspath(path)
    return os.getcwd()


def _run_status(args: argparse.Namespace) -> int:
    """Run the status command."""
    config = load_config()
    root = _resolve_path(args.path)
    depth = args.depth or config.depth
    use_color = args.color if args.color is not None else _detect_color()
    fmt = args.format or "auto"

    try:
        repos = scan_repos(root, max_depth=depth, skip_set=config.skip_set)
    except PermissionError as e:
        print_error(f"Cannot scan {root}: {e}")
        return 1

    if not repos:
        if fmt == "json":
            from .output import print_status_json
            print_status_json([])
        else:
            print(f"No git repositories found under {root}")
        return 0

    repos = enrich_all(repos, timeout=config.timeout)

    # Filter: dirty only
    if getattr(args, 'dirty', False):
        repos = [r for r in repos if r.is_dirty or r.error]

    # Filter: ahead only
    if getattr(args, 'ahead', False):
        repos = [r for r in repos if r.ahead > 0 or r.behind > 0 or r.error]

    if fmt == "json":
        print_status(repos, use_color=False, output_format="json")
    else:
        print(f"\n  {_DIM if use_color else ''}Scanning:{_RESET if use_color else ''} {root} {_DIM if use_color else ''}(depth: {depth}){_RESET if use_color else ''}\n")
        print_status(repos, use_color=use_color)

    return 0


def _run_pull(args: argparse.Namespace) -> int:
    """Run the pull command."""
    config = load_config()
    root = _resolve_path(args.path)
    depth = args.depth or config.depth
    use_color = args.color if args.color is not None else _detect_color()

    try:
        repos = scan_repos(root, max_depth=depth, skip_set=config.skip_set)
    except PermissionError as e:
        print_error(f"Cannot scan {root}: {e}")
        return 1

    repos = enrich_all(repos, timeout=config.timeout)

    if not repos:
        print(f"No git repositories found under {root}")
        return 0

    print(f"\nPulling {len(repos)} repos under {root}...\n")

    # Only pull repos that have a remote and no error
    pullable = [r for r in repos if r.has_remote and not r.error]
    if not pullable:
        print("  No repos with remotes to pull.")
        return 0

    results = pull_repos(pullable, strategy=args.strategy or "ff-only",
                         timeout=config.timeout, dry_run=args.dry_run)
    print_operations(results, use_color=use_color)

    return 0 if all(r.success for r in results) else 1


def _run_fetch(args: argparse.Namespace) -> int:
    """Run the fetch command."""
    config = load_config()
    root = _resolve_path(args.path)
    depth = args.depth or config.depth
    use_color = args.color if args.color is not None else _detect_color()

    try:
        repos = scan_repos(root, max_depth=depth, skip_set=config.skip_set)
    except PermissionError as e:
        print_error(f"Cannot scan {root}: {e}")
        return 1

    repos = enrich_all(repos, timeout=config.timeout)

    fetchable = [r for r in repos if r.has_remote and not r.error]
    if not fetchable:
        print(f"No git repositories with remotes found under {root}")
        return 0

    print(f"\nFetching {len(fetchable)} repos under {root}...\n")
    results = fetch_repos(fetchable, timeout=config.timeout, dry_run=args.dry_run)
    print_operations(results, use_color=use_color)

    return 0 if all(r.success for r in results) else 1


def _run_gc(args: argparse.Namespace) -> int:
    """Run the gc command."""
    config = load_config()
    root = _resolve_path(args.path)
    depth = args.depth or config.depth
    use_color = args.color if args.color is not None else _detect_color()

    try:
        repos = scan_repos(root, max_depth=depth, skip_set=config.skip_set)
    except PermissionError as e:
        print_error(f"Cannot scan {root}: {e}")
        return 1

    repos = enrich_all(repos, timeout=config.timeout)

    eligible = [r for r in repos if not r.error]
    if not eligible:
        print(f"No git repositories found under {root}")
        return 0

    print(f"\nRunning gc on {len(eligible)} repos...\n")
    results = gc_repos(eligible, aggressive=args.aggressive,
                       timeout=config.timeout, dry_run=args.dry_run)
    print_operations(results, use_color=use_color)

    return 0 if all(r.success for r in results) else 1


def _run_dirty(args: argparse.Namespace) -> int:
    """Show only dirty repos."""
    args.dirty = True
    return _run_status(args)


def _run_ahead(args: argparse.Namespace) -> int:
    """Show only repos ahead/behind."""
    args.ahead = True
    return _run_status(args)


def _run_summary(args: argparse.Namespace) -> int:
    """Print a compact one-line summary."""
    config = load_config()
    root = _resolve_path(args.path)
    depth = args.depth or config.depth

    try:
        repos = scan_repos(root, max_depth=depth, skip_set=config.skip_set)
    except PermissionError as e:
        print_error(f"Cannot scan {root}: {e}")
        return 1

    repos = enrich_all(repos, timeout=config.timeout)
    print_summary(repos)
    return 0


def _run_self_test() -> int:
    """Run comprehensive self-test."""
    import tempfile
    import shutil
    import subprocess

    print("gittree self-test")
    print("=" * 40)
    passed = 0
    failed = 0

    def _check(description: str, condition: bool, detail: str = ""):
        nonlocal passed, failed
        if condition:
            print(f"  ✓ {description}")
            passed += 1
        else:
            print(f"  ✗ {description} — {detail}")
            failed += 1

    # Create a temp directory with test repos
    tmpdir = tempfile.mkdtemp(prefix="gittree-test-")

    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        _check("git is installed", True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        _check("git is installed", False, "git not found")
        shutil.rmtree(tmpdir)
        return 1

    # Create test repos
    repo_paths = []
    for name in ["repo-clean", "repo-dirty", "repo-unpushed", "repo-empty", "repo-bare"]:
        p = os.path.join(tmpdir, name)
        os.makedirs(p)
        subprocess.run(["git", "init"], cwd=p, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=p, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=p, capture_output=True)
        repo_paths.append(p)

    # repo-clean: committed + clean
    clean_path = os.path.join(tmpdir, "repo-clean")
    with open(os.path.join(clean_path, "readme.md"), "w") as f:
        f.write("# Clean Repo")
    subprocess.run(["git", "add", "."], cwd=clean_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial commit"], cwd=clean_path, capture_output=True)

    # repo-dirty: uncommitted changes
    dirty_path = os.path.join(tmpdir, "repo-dirty")
    with open(os.path.join(dirty_path, "readme.md"), "w") as f:
        f.write("# Dirty Repo")
    subprocess.run(["git", "add", "."], cwd=dirty_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial commit"], cwd=dirty_path, capture_output=True)
    with open(os.path.join(dirty_path, "untracked.txt"), "w") as f:
        f.write("new file")
    with open(os.path.join(dirty_path, "readme.md"), "a") as f:
        f.write("\nmodified")

    # repo-unpushed: commit ahead of empty remote (we'll just have a commit with no remote)
    unpushed_path = os.path.join(tmpdir, "repo-unpushed")
    with open(os.path.join(unpushed_path, "readme.md"), "w") as f:
        f.write("# Unpushed Repo")
    subprocess.run(["git", "add", "."], cwd=unpushed_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "initial commit\n\nThis is a longer commit message for testing.\nMultiple lines."], cwd=unpushed_path, capture_output=True)

    # repo-empty: initialized but no commits
    # (already initialized above)

    # Also create a non-git directory to test filtering
    os.makedirs(os.path.join(tmpdir, "not-a-repo"))

    # Now test gittree scanner directly
    from .scanner import scan_repos, RepoInfo
    from .status import enrich_repo

    # 1. Test scanner
    repos = scan_repos(tmpdir, max_depth=3)
    _check("scanner finds repos", len(repos) >= 4,
           f"Found {len(repos)} repos, expected >= 4")

    repo_names = {r.name for r in repos}
    _check("scanner finds repo-clean", "repo-clean" in repo_names)
    _check("scanner finds repo-dirty", "repo-dirty" in repo_names)
    _check("scanner finds repo-unpushed", "repo-unpushed" in repo_names)
    _check("scanner skips non-git dirs", "not-a-repo" not in repo_names)

    # 2. Test status enrichment
    for repo in repos:
        enrich_repo(repo)

    # Find specific repos
    def _find(name):
        for r in repos:
            if r.name == name:
                return r
        return None

    clean = _find("repo-clean")
    dirty = _find("repo-dirty")
    unpushed = _find("repo-unpushed")

    if clean:
        _check("clean repo detected as clean", not clean.is_dirty and not clean.error)
        _check("clean repo has branch", clean.branch is not None)

    if dirty:
        _check("dirty repo detected as dirty", dirty.is_dirty)
        _check("dirty repo has untracked files", dirty.untracked > 0)

    if unpushed:
        _check("unpushed repo has commit", unpushed.last_commit is not None)
        _check("unpushed repo has branch", unpushed.branch is not None)

    # 3. Test JSON output
    from .output import print_status_json
    import io
    json_out = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = json_out
    try:
        print_status_json(repos)
        json_data = json.loads(json_out.getvalue())
        _check("JSON output valid", "repos" in json_data and "summary" in json_data)
        _check("JSON summary has total", json_data["summary"]["total"] >= 4)
    finally:
        sys.stdout = old_stdout

    # 4. Test with a non-existent directory
    repos_empty = scan_repos("/nonexistent/path")
    _check("scanner handles missing path", len(repos_empty) == 0)

    # 5. Test with a file path
    repos_file = scan_repos("/etc/hostname")
    _check("scanner handles file path", len(repos_file) == 0)

    print()
    print(f"Results: {passed} passed, {failed} failed")
    shutil.rmtree(tmpdir)
    return 0 if failed == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="gittree",
        description="Git Repository Tree Manager — scan, inspect, and operate on multiple git repos in bulk.",
        epilog="Zero external dependencies. Python stdlib only.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"gittree v{__version__}")
    parser.add_argument("--test", action="store_true", help="Run self-test suite")
    parser.add_argument("--color", choices=["auto", "always", "never"], default="auto",
                        help="Color output (default: auto)")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # status
    p_status = subparsers.add_parser("status", help="Show status of all repos")
    p_status.add_argument("path", nargs="?", default=None, help="Root directory to scan")
    p_status.add_argument("--depth", type=int, default=None, help="Max directory depth")
    p_status.add_argument("--format", choices=["auto", "json"], default="auto", help="Output format")
    p_status.add_argument("--dirty", action="store_true", help="Show only dirty repos")
    p_status.add_argument("--ahead", action="store_true", help="Show only ahead/behind repos")

    # dirty
    p_dirty = subparsers.add_parser("dirty", help="Show only repos with uncommitted changes")
    p_dirty.add_argument("path", nargs="?", default=None, help="Root directory to scan")
    p_dirty.add_argument("--depth", type=int, default=None, help="Max directory depth")
    p_dirty.add_argument("--format", choices=["auto", "json"], default="auto", help="Output format")

    # ahead
    p_ahead = subparsers.add_parser("ahead", help="Show only repos ahead/behind remote")
    p_ahead.add_argument("path", nargs="?", default=None, help="Root directory to scan")
    p_ahead.add_argument("--depth", type=int, default=None, help="Max directory depth")
    p_ahead.add_argument("--format", choices=["auto", "json"], default="auto", help="Output format")

    # pull
    p_pull = subparsers.add_parser("pull", help="Pull all repos (with stash if dirty)")
    p_pull.add_argument("path", nargs="?", default=None, help="Root directory to scan")
    p_pull.add_argument("--depth", type=int, default=None, help="Max directory depth")
    p_pull.add_argument("--strategy", choices=["ff-only", "rebase", "merge"], default="ff-only",
                        help="Pull strategy (default: ff-only)")
    p_pull.add_argument("--dry-run", action="store_true", help="Simulate without pulling")

    # fetch
    p_fetch = subparsers.add_parser("fetch", help="Fetch all repos")
    p_fetch.add_argument("path", nargs="?", default=None, help="Root directory to scan")
    p_fetch.add_argument("--depth", type=int, default=None, help="Max directory depth")
    p_fetch.add_argument("--dry-run", action="store_true", help="Simulate without fetching")

    # gc
    p_gc = subparsers.add_parser("gc", help="Run git gc on all repos")
    p_gc.add_argument("path", nargs="?", default=None, help="Root directory to scan")
    p_gc.add_argument("--depth", type=int, default=None, help="Max directory depth")
    p_gc.add_argument("--aggressive", action="store_true", help="Aggressive gc")
    p_gc.add_argument("--dry-run", action="store_true", help="Simulate without gc")

    # summary
    p_summary = subparsers.add_parser("summary", help="Compact one-line summary")
    p_summary.add_argument("path", nargs="?", default=None, help="Root directory to scan")
    p_summary.add_argument("--depth", type=int, default=None, help="Max directory depth")

    return parser


def main():
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args()

    # Handle color flag
    if args.color == "never":
        args.color = False
    elif args.color == "always":
        args.color = True
    else:
        args.color = None  # auto-detect

    # Self-test
    if args.test:
        sys.exit(_run_self_test())

    # Handle commands
    if args.command == "status" or args.command is None:
        sys.exit(_run_status(args))
    elif args.command == "pull":
        sys.exit(_run_pull(args))
    elif args.command == "fetch":
        sys.exit(_run_fetch(args))
    elif args.command == "gc":
        sys.exit(_run_gc(args))
    elif args.command == "dirty":
        sys.exit(_run_dirty(args))
    elif args.command == "ahead":
        sys.exit(_run_ahead(args))
    elif args.command == "summary":
        sys.exit(_run_summary(args))
    else:
        parser.print_help()
        sys.exit(1)
