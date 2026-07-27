"""Git status parser — query individual repo state via git porcelain."""

import subprocess
import os
from .scanner import RepoInfo


def _git(*args: str, cwd: str, timeout: int = 30) -> tuple[int, str, str]:
    """Run a git command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except FileNotFoundError:
        return -2, "", "git not found"
    except OSError as e:
        return -3, "", str(e)


def _is_inside_worktree(repo: RepoInfo) -> bool:
    """Check if .git is a file (git worktree) rather than a directory."""
    git_path = os.path.join(repo.path, ".git")
    return os.path.isfile(git_path)


def enrich_repo(repo: RepoInfo, timeout: int = 30) -> RepoInfo:
    """Query git status for a single repo and populate RepoInfo fields.

    Runs multiple git commands to gather:
      - Current branch (or detached HEAD)
      - Remote URL
      - Ahead/behind counts
      - Dirty state (staged, unstaged, untracked)
      - Last commit message + date
    """
    if not os.path.isdir(repo.path):
        repo.error = "Directory not found"
        return repo

    if not os.path.exists(os.path.join(repo.path, ".git")):
        repo.error = "Not a git repository (no .git)"
        return repo

    # 1. Branch name
    rc, out, _ = _git("branch", "--show-current", cwd=repo.path, timeout=timeout)
    if rc != 0:
        # Try detached HEAD
        rc2, out2, _ = _git("log", "--oneline", "-1", cwd=repo.path, timeout=timeout)
        if rc2 == 0:
            repo.branch = f"HEAD ({out2.split()[0][:8] if out2.strip() else 'detached'})"
            # Check if rebasing
            if os.path.isdir(os.path.join(repo.path, ".git", "rebase-merge")):
                repo.branch = f"(rebasing) {repo.branch}"
        else:
            repo.error = f"git branch failed: {out.strip() or 'unknown error'}"
            return repo
    else:
        repo.branch = out.strip() or "HEAD"

    # 2. Remote URL
    rc, out, _ = _git("remote", "get-url", "origin", cwd=repo.path, timeout=timeout)
    if rc == 0:
        repo.remote_url = out.strip()
        repo.has_remote = True
    else:
        # Try to detect if there IS a remote configured
        rc2, out2, _ = _git("remote", "-v", cwd=repo.path, timeout=timeout)
        if rc2 == 0 and out2.strip():
            # Extract first remote URL
            for line in out2.strip().split("\n"):
                parts = line.split()
                if len(parts) >= 2:
                    repo.remote_url = parts[1]
                    repo.has_remote = True
                    break

    # 3. Ahead/behind (requires remote tracking branch)
    if repo.branch and repo.branch.startswith("HEAD"):
        # Detached HEAD — can't check ahead/behind meaningfully
        pass
    elif repo.has_remote:
        rc, out, _ = _git(
            "rev-list", "--left-right", "--count",
            f"{repo.branch}@{{upstream}}...{repo.branch}",
            cwd=repo.path, timeout=timeout
        )
        if rc == 0 and out.strip():
            parts = out.strip().split()
            if len(parts) == 2:
                try:
                    repo.behind = int(parts[0])
                    repo.ahead = int(parts[1])
                except ValueError:
                    pass
        # If upstream not configured, out will be empty — that's fine

    # 4. Dirty state via --porcelain
    rc, out, _ = _git("status", "--porcelain", cwd=repo.path, timeout=timeout)
    if rc == 0:
        for line in out.strip().split("\n"):
            if not line.strip():
                continue
                # Parse two-character status code
            if len(line) < 3:
                continue
            code = line[:2]
            if code == "??":
                repo.untracked += 1
            elif " " in code and code.strip():
                # Index staging area
                if code[0] != " " and code[0] != "?":
                    repo.staged += 1
                # Working tree
                if code[1] != " " and code[1] != "?":
                    repo.unstaged += 1
    repo.is_dirty = (repo.staged + repo.unstaged + repo.untracked) > 0

    # 5. Last commit info
    rc, out, _ = _git("log", "--oneline", "-1", cwd=repo.path, timeout=timeout)
    if rc == 0 and out.strip():
        repo.last_commit = out.strip()
    rc, out, _ = _git(
        "log", "-1", "--format=%ai", cwd=repo.path, timeout=timeout
    )
    if rc == 0 and out.strip():
        repo.last_commit_date = out.strip()[:19]  # YYYY-MM-DD HH:MM:SS

    return repo


def enrich_all(repos: list[RepoInfo], timeout: int = 30) -> list[RepoInfo]:
    """Enrich all repos in the list, collecting errors."""
    results: list[RepoInfo] = []
    for repo in repos:
        try:
            results.append(enrich_repo(repo, timeout=timeout))
        except Exception as e:
            repo.error = str(e)
            results.append(repo)
    return results
