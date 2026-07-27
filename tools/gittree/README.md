# gittree

**Git Repository Tree Manager — scan, inspect, and operate on multiple git repos in bulk.**

Say goodbye to `cd`-ing into every project directory to run `git status` or `git pull` individually. `gittree` scans entire directory trees, finds all git repositories, and gives you a clean bird's-eye view of their state — all in one command.

Zero external dependencies. Python stdlib only.

## Features

- **Bulk status** — See the branch, dirty state, ahead/behind count, and last commit of every repo at a glance
- **Bulk pull** — Pull all repos with automatic stash/unstash for dirty working trees
- **Bulk fetch** — Fetch all remotes non-destructively
- **Bulk gc** — Run garbage collection across repos
- **Smart filtering** — `dirty` shows only repos with changes; `ahead` shows only repos with unpushed commits
- **JSON output** — `--format json` for scripting and CI/CD integration
- **Color-coded** — Green (clean), yellow (dirty), cyan (ahead), red (error)
- **Configurable** — Depth, skip dirs, color via env vars or `.gittreerc`
- **Self-test** — `gittree --test` runs a comprehensive test suite

## Quick Start

```bash
# Clone + run (no install needed)
git clone https://github.com/zwart04/gittree.git
cd gittree
python3 -m gittree status /your/projects

# Or install via pip
pip install -e .
gittree status /your/projects

# Or just copy the src/gittree directory — it's self-contained
```

## Usage

### Status

```bash
# Show all repos under current directory
gittree status

# Scan a specific directory with custom depth
gittree status /root --depth 4

# JSON output for scripting
gittree status /root --format json

# Only show dirty repos
gittree dirty

# Only show repos ahead/behind remote
gittree ahead

# Compact one-line summary
gittree summary
```

### Bulk Operations

```bash
# Pull all repos (ff-only, safe default)
gittree pull

# Pull with rebase strategy
gittree pull --strategy rebase

# Fetch all remotes
gittree fetch

# Run garbage collection
gittree gc

# Aggressive gc (slower, more thorough)
gittree gc --aggressive

# Dry-run to see what would happen
gittree pull --dry-run
```

### Output Example

```
  Scanning: /root (depth: 3)

  ✓ daily-apps/2026-06-22-gittree    main      ✓  clean
  ✗ hermes-agent                     develop   ●  dirty(?1)  fd3a8b42 fix: typo
  ↑ 9router                           main      ↑  ahead 2   v0.5.4 release prep
  ✓ n8n                              master    ✓  clean
  ✓ homepage                          main      ✓  clean
  ○ server-monitor                    main      ○  no-remote

  6 repos, 4 clean, 1 dirty, 1 ahead
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `GITTREE_DEPTH` | Max directory depth to scan | `3` |
| `GITTREE_TIMEOUT` | Git command timeout (seconds) | `30` |
| `GITTREE_COLOR` | Enable/disable color output | `auto` (detect TTY) |
| `GITTREE_SKIP_DIRS` | Comma-separated dirs to skip | `node_modules,.cache,...` |
| `GITTREE_RC` | Path to `.gittreerc` config file | — |
| `NO_COLOR` | Standard flag to disable color | — |

## Architecture

```
src/gittree/
├── __init__.py     # Package metadata
├── __main__.py     # python3 -m gittree entry point
├── cli.py          # Argument parser, commands, main()
├── config.py       # Config loader (env vars + .gittreerc)
├── scanner.py      # Directory scanner — find git repos
├── status.py       # Git status parser — query individual repos
├── operations.py   # Bulk git operations (pull, fetch, gc)
└── output.py       # Formatted output (plain, color, JSON)
```

## Design Philosophy

1. **Zero dependencies** — Python stdlib only. Install and run anywhere Python 3.10+ is available. No `pip install rich`, no `colorama`, no `requests`.

2. **Fail gracefully, continue others** — If one repo has an error, gittree reports it and continues with the rest. A single corrupted repo doesn't block the entire operation.

3. **Predictable output** — Consistent formatting across all commands. `--format json` for machines, color-coded terminal for humans. Always includes a summary line.

4. **Safe defaults** — Pull uses `--ff-only` by default (won't create merge commits). Dirty repos are automatically stashed before pull. `--dry-run` available for all operations.

## License

MIT
