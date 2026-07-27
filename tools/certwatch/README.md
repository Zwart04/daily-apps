# certwatch

**SSL/TLS certificate expiry checker — beautiful CLI, bulk async checks, JSON output, Nagios-compatible.**

Stop relying on fragile bash one-liners or bloated TLS scanners. certwatch gives you a single-purpose, production-grade tool for checking when your SSL certificates expire.

## Features

- Single command: `certwatch example.com`
- Bulk async checks: check hundreds of domains in seconds
- JSON, YAML, and Nagios/Icinga output modes
- Beautiful Rich terminal output with color-coded status
- Custom warning/critical thresholds (`--warn 30 --crit 7`)
- Auto-detects port, supports `domain:port` syntax
- SNI support on every connection
- OCSP stapling detection
- TLS version reporting
- Zero hardcoded config — environment-driven
- Nagios-compatible exit codes for monitoring integration
- Read from file or stdin for pipeline use

## Quick Start

### Using pip

```bash
pip install certwatch
certwatch example.com
```

### From Source

```bash
git clone https://github.com/Zwart04/certwatch.git
cd certwatch
pip install -e .
certwatch example.com
```

## Usage

### Basic Checks

```bash
# Single domain
certwatch example.com

# Multiple domains
certwatch example.com google.com github.com

# Custom ports
certwatch example.com:8443 myservice.internal:9090

# From file (one domain per line)
certwatch --file domains.txt

# From stdin
cat domains.txt | certwatch --file -
```

### Output Formats

```bash
# JSON output
certwatch --json example.com

# YAML output (requires PyYAML)
certwatch --yaml example.com

# Nagios/Icinga compatible output
certwatch --nagios example.com
```

### Thresholds

```bash
# Warn at 30 days, critical at 7 days (defaults)
certwatch example.com

# Custom thresholds
certwatch --warn 60 --crit 14 example.com
```

### Detailed View

```bash
# Show all certificates, including healthy ones
certwatch --all example.com google.com

# Detailed per-certificate info
certwatch --detail example.com
```

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `CERTWATCH_WARN_DAYS` | Warning threshold in days | 30 |
| `CERTWATCH_CRIT_DAYS` | Critical threshold in days | 7 |
| `CERTWATCH_TIMEOUT` | Connection timeout in seconds | 10 |
| `CERTWATCH_CONCURRENT` | Max concurrent async checks | 50 |
| `CERTWATCH_VERBOSE` | Enable verbose logging | false |

## API / Usage

### As a Library

```python
from certwatch.checker import check_certificate, check_certificates_async, parse_targets
from certwatch.config import Config
import asyncio

# Single check
result = check_certificate("example.com")
print(f"{result.hostname}: {result.status} ({result.days_remaining}d)")

# Bulk async check
config = Config.from_env()
targets = parse_targets(["example.com", "google.com", "github.com"])
results = asyncio.run(check_certificates_async(targets, config))
for r in results.results:
    print(f"{r.hostname}: {r.status}")
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All certificates valid |
| 1 | Warning or error (some certs expiring soon) |
| 2 | Critical or expired (certs expiring or already expired) |
| 130 | Interrupted by user |

## Architecture

```
certwatch/
├── src/certwatch/
│   ├── __init__.py     # Package metadata
│   ├── __main__.py     # `python -m certwatch` entry
│   ├── cli.py          # CLI arg parsing + orchestration
│   ├── checker.py      # Core SSL check logic (sync + async)
│   ├── config.py       # Env-driven configuration
│   ├── output.py       # Rich/JSON/YAML/Nagios formatting
│   └── types.py        # Data classes (CertInfo, CheckResult)
├── tests/
├── pyproject.toml
├── README.md
├── LICENSE
└── test.sh
```

### Key Design Decisions

- **stdlib + 2 dependencies**: Uses `argparse` (stdlib) for CLI, `rich` for beautiful output, `cryptography` for cert parsing. No framework bloat.
- **Async bulk checks**: Uses `asyncio` + `concurrent.futures` to check hundreds of domains in parallel.
- **Fail loudly**: Every socket/SSL/network error is caught and reported. No silent failures.
- **Zero hardcoded secrets**: All config via env vars or CLI flags.
- **Nagios-native**: `--nagios` mode with proper exit codes for drop-in monitoring replacement.

## Design Philosophy

1. **Single responsibility** — certwatch does one thing (check SSL expiry) and does it perfectly. It is not a full TLS scanner.
2. **CLI-first, library-second** — The CLI is the primary interface. The Python API is a bonus.
3. **Beautiful by default** — Terminal output uses rich typography and color. JSON/YAML for automation.
4. **Bulk by design** — Async from day one. No sequential loops.
5. **Configurable, not complicated** — Sensible defaults, env var overrides, CLI flag overrides.

## License

MIT
