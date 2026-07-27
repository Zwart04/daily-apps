# gittree Architecture

## Overview
Zero-dependency Python CLI for bulk git repository management. Scans directory trees for git repos and provides status overview, bulk operations, and clean output.

## Directory Structure
```
2026-06-22-gittree/
├── src/
│   ├── __init__.py
│   ├── __main__.py        # python3 -m gittree entry point
│   ├── cli.py             # Argument parser + main()
│   ├── scanner.py         # Find git repos in directory tree
│   ├── status.py          # Parse git status for each repo
│   ├── operations.py      # Bulk git operations (pull, fetch, gc)
│   ├── output.py          # Formatted output (plain, color, JSON, table)
│   └── config.py          # Config from env vars + .gittreerc
├── README.md
├── LICENSE                # MIT
├── pyproject.toml
└── test.sh                # Self-test script
```

## Module Responsibilities

### cli.py
- Argument parser (argparse, stdlib)
- Commands: status, pull, fetch, dirty, summary
- Global flags: --json, --no-color, --depth, --test
- Configures logging
- Calls appropriate module based on command

### scanner.py
- `scan_repos(root_dir, max_depth)` → list of RepoInfo objects
- Detects .git directories
- Respects max_depth (default: 3 levels)
- Skips common non-code dirs (node_modules, .cache, venv, .git)
- Returns: path, name, remote_url, branch, is_dirty

### status.py
- `get_repo_status(repo_path)` → dict with:
  - branch, ahead, behind, staged, unstaged, untracked, last_commit, last_commit_date
- Parses `git status --porcelain` and `git branch -v`
- Handles edge cases: detached HEAD, initial commit, bare repo

### operations.py
- `pull_repos(repos, strategy)` → results per repo
- `fetch_repos(repos)` → results per repo
- `gc_repos(repos)` → results per repo
- Error handling per repo (one failure doesn't stop others)
- Dry-run mode (`--dry-run`)

### output.py
- `print_status(repos, format, color)` 
- Formats: plain text, colored terminal, JSON, table
- Colored indicators: green (clean), yellow (uncommitted), red (unpushed), cyan (ahead)
- Summary line: "8 repos found, 3 clean, 2 dirty, 1 unpushed, 2 ahead"

### config.py
- `load_config()` → Config object
- Reads from env vars (GITTREE_DEPTH, GITTREE_COLOR, etc.)
- Reads from .gittreerc in scanned directory
- Sensible defaults

## Zero Dependencies
- Python stdlib only: argparse, json, os, subprocess, sys, datetime, pathlib
- ANSI color codes hardcoded (no colorama/rich)
- All git operations via subprocess.run

## Error Handling
- If git is not installed → clear error message
- If a repo has corruption → error for that repo, continue others
- Permission denied → skip with warning
- Timeout per operation (30s default) → skip with error

## Output Examples
```
$ gittree status
📂 Scanning /root (depth: 3)...
  ✓ daily-apps/2026-06-22-gittree    main      ✔ clean
  ✓ daily-apps/2026-06-19-toolkit    main      ● 1 unpushed
  ✓ hermes-agent                      develop   ✗ 2 uncommitted
  ✓ homepage                          main      ✔ clean
  ⚠ n8n                              master    ✗ 3 untracked
  ✓ server-monitor                    main      ✔ clean
  ✓ .9router                          main      ● ahead 2

6 repos, 3 clean, 1 dirty, 1 unpushed, 1 ahead
```

```
$ gittree status --json
{"repos": [...], "summary": {"total": 6, "clean": 3, "dirty": 1, "unpushed": 1, "ahead": 1}}
```

## Self-Test
- `gittree --test` or `python3 -m gittree --test`
- Creates temp dirs with test git repos
- Tests all commands
- Cleans up after
