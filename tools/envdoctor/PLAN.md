# envdoctor — Environment Variable Diagnostic CLI

## Problem Statement
Every software project uses environment variables for configuration — API keys, database URLs, secrets, feature flags. Yet there is no standard tool to:
- Discover ALL environment variables a project needs (across source code, docker files, shell scripts)
- Validate that .env files provide all required vars
- Detect unused vars in .env.example (documentation rot)
- Identify hardcoded secrets that should be env vars
- Generate proper .env.example from actual usage

Existing solutions only load env vars (`dotenv`, `direnv`) or manage encrypted sync (`dotenv-vault`). None do comprehensive DIAGNOSTICS.

## Why This Matters
Every developer has wasted hours debugging "missing env var" issues. Every project has .env.example that's out of sync with actual code. envdoctor solves this in one CLI command.

## Architecture

```
envdoctor/
├── envdoctor/
│   ├── __init__.py          # Package entry, version
│   ├── __main__.py          # `python -m envdoctor` support
│   ├── cli.py               # Argument parser, main entry point
│   ├── scanner.py           # Source file scanner for env var patterns
│   ├── parser.py            # Parse .env and .env.example files
│   ├── analyzer.py          # Cross-reference engine (used vs defined)
│   ├── reporter.py          # Output formatting (text, JSON, markdown)
│   ├── secrets.py           # Heuristic secret detection
│   ├── fixer.py             # Auto-generate .env.example, suggest fixes
│   └── types.py             # Type definitions
├── test.sh                  # Self-test
├── README.md                # Full documentation
├── LICENSE                  # MIT
└── .gitignore
```

## Data Flow
1. Scan directory → collect all files matching known patterns
2. For each file, extract env var references using regex patterns
3. Load .env and .env.example files → parse key=value pairs
4. Cross-reference: used_vars ∩ defined_vars, used_vars - defined_vars, defined_vars - used_vars
5. Scan for hardcoded secrets (strings that look like API keys, tokens, passwords)
6. Generate report + auto-fix suggestions

## Zero Dependencies
Python stdlib only: argparse, json, os, re, sys, pathlib, itertools, collections

## Quality Gates
- [x] Problem validated (Phase 0)
- [ ] Modular architecture (file per concern)
- [ ] Type hints throughout
- [ ] Config via args + env, zero hardcode
- [ ] Error handling at every IO boundary
- [ ] --test self-test suite
- [ ] --json output for CI integration
- [ ] README with full format
- [ ] MIT License
