# envdoctor

**Environment Variable Diagnostic Tool — scan, validate, and document every env var across your project.**

envdoctor is a zero-dependency Python CLI that scans your entire codebase to discover all environment variable references across languages (Python, Node.js, Go, Shell, Docker, YAML, Java, Ruby, PHP, .NET, Terraform, and more), cross-references them with your `.env` and `.env.example` files, detects hardcoded secrets, and generates actionable reports.

No more "missing env var" bugs at 2 AM. No more `.env.example` rot. No more committed API keys.

## Features

- **Multi-language scanning** — 20+ language patterns for os.environ, process.env, $VAR, ${VAR}, System.getenv, and more
- **Smart .env analysis** — detects missing vars, empty placeholders, commented-out entries, stale documentation
- **Secret detection** — finds hardcoded API keys, tokens, passwords, connection strings, AWS keys, and JWT tokens
- **Three output formats** — colorized terminal (human-readable), JSON (CI integration), Markdown (documentation)
- **Auto-fix mode** — `--fix` generates `.env.example` from actual code usage
- **Health scoring** — quantitative score (0-100) for your env var hygiene
- **Zero dependencies** — pure Python stdlib, install and run instantly
- **CI-ready** — returns non-zero exit code when issues found, JSON for GitHub Actions / GitLab CI

## Quick Start

### Using pip

```bash
pip install envdoctor
envdoctor .
```

### From Source

```bash
git clone https://github.com/Zwart04/envdoctor.git
cd envdoctor
python3 -m envdoctor /path/to/your/project
```

### One-shot (no install)

```bash
python3 -m envdoctor .
```

## Usage

```bash
# Scan current directory
envdoctor .

# Scan specific project
envdoctor /path/to/project

# JSON output (for CI)
envdoctor . --json

# Markdown report
envdoctor . --markdown

# Generate .env.example from code usage
envdoctor . --fix

# Verbose output with file locations
envdoctor . --verbose

# Run self-test
envdoctor --test
```

## Output Examples

### Terminal (default)
```
🔍 envdoctor — Environment Variable Diagnostic
============================================================
Project   : /home/user/project
Files     : 1,247 scanned
Issues    : 3
Health    : 82/100

📊 Summary
  Environment variables referenced in code: 47 (23 unique)
  Vars defined in .env:                   18
  Vars defined in .env.example:           20

❌ Missing from .env (5)
  These vars are used in code but NOT defined in .env
    • DATABASE_URL
    • REDIS_HOST
    • JWT_SECRET

📌 Stale in .env.example (2)
    • OLD_API_KEY
    • DEPRECATED_TOKEN

Health Score: 82/100 — Good shape!
```

### JSON (CI-friendly)
```json
{
  "version": "1.0.0",
  "summary": {
    "files_scanned": 1247,
    "health_score": 82.0,
    "vars_referenced_in_code": 23
  },
  "issues": {
    "missing_from_env": ["DATABASE_URL", "REDIS_HOST", "JWT_SECRET"],
    "missing_from_env_count": 3
  }
}
```

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `ENVDOCTOR_MAX_FILES` | `5000` | Maximum files to scan |
| `ENVDOCTOR_NO_COLOR` | `false` | Disable ANSI colors |

All configuration is via command-line arguments. No config file needed.

## Supported Languages & Patterns

| Language | Patterns Detected |
|----------|------------------|
| **Python** | `os.environ.get('X')`, `os.getenv('X')`, `os.environ['X']` |
| **Node.js / JS/TS** | `process.env.X`, `process.env['X']` |
| **Shell** | `$VAR`, `${VAR}`, `${VAR:-default}` |
| **Docker / Docker Compose** | `${VAR}`, `ENV VAR` |
| **Go** | `os.Getenv("X")` |
| **Java / Spring** | `System.getenv("X")`, `@Value("${X}")` |
| **Ruby** | `ENV['X']` |
| **PHP** | `getenv('X')`, `$_ENV['X']` |
| **.NET / C#** | `Environment.GetEnvironmentVariable("X")` |
| **Terraform** | `var.X` |
| **Kubernetes** | `$(X)` |
| **GitHub Actions** | `${{ env.X }}`, `${{ secrets.X }}` |
| **Ansible** | `lookup('env', 'X')` |
| **Deno** | `Deno.env.get('X')` |

## Architecture

```
envdoctor/
├── envdoctor/
│   ├── __init__.py     # Package entry, version
│   ├── __main__.py     # python -m envdoctor support
│   ├── cli.py          # Argument parser, main entry
│   ├── scanner.py      # Source file scanner for env var patterns
│   ├── parser.py       # Parse .env and .env.example files
│   ├── analyzer.py     # Cross-reference engine
│   ├── reporter.py     # Output formatting (text, JSON, markdown)
│   ├── fixer.py        # Auto-generate .env.example
│   └── types.py        # Type definitions
├── test.sh             # Self-test script
├── README.md
└── LICENSE
```

### Data Flow
```
Source Files ──► Scanner ──► env_var_refs ──┐
                                            ├──► Analyzer ──► Reporter ──► Output
.env Files ────► Parser ──► dotenv_entries ─┘
                                                    │
                                              Secrets Detected ──► Warnings
```

## Design Philosophy

1. **Zero friction** — No dependencies, no config file, one command to run. `pip install && envdoctor .` or just `python3 -m envdoctor .`.
2. **Comprehensive by default** — Scans the whole directory, detects all patterns, no explicit configuration needed for common setups.
3. **CI-native** — JSON output and non-zero exit codes mean it integrates natively into GitHub Actions, GitLab CI, pre-commit hooks, and deployment pipelines.
4. **Helpful, not noisy** — Prioritizes actionable issues (missing vars, hardcoded secrets) over noise. Sections that pass are summarized quietly.
5. **Progressive disclosure** — `envdoctor .` for a quick check, `--verbose` for details, `--json` for automation, `--fix` to auto-remediate.

## Continuous Integration

### GitHub Actions
```yaml
- name: Check environment variables
  run: |
    pip install envdoctor
    envdoctor . --json | tee env_report.json
    # exit code 1 if issues found
```

### Pre-commit Hook
```yaml
repos:
  - repo: https://github.com/Zwart04/envdoctor
    rev: v1.0.0
    hooks:
      - id: envdoctor
```

## License

MIT

---

*Built with Hermes Agent — daily app builder*
