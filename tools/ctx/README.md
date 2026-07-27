# ctx

**Codebase Context Extractor for AI coding assistants.**

Extract your codebase structure and file contents into a clean,
copy-paste-ready format for use with ChatGPT, Claude, Copilot, and
other AI coding tools. Zero external dependencies.

Stop manually running `tree`, `cat`, and counting tokens. One command
gives your AI assistant everything it needs to understand your project.

```bash
pip install ctx
ctx .
# Output: markdown with directory tree + file contents + token count
```

## Features

- **Directory scanning** with automatic `.gitignore` awareness
- **Dual interface** — CLI (`python3 -m ctx .`) and Python API (`from ctx import extract`)
- **Three output formats** — Markdown (default, best for AI chats), Plain, JSON
- **Token counting** — character-based estimate by default; exact per-model when `tiktoken` is installed
- **Binary detection** — automatically skips images, archives, executables, and other binary files
- **Encoding resilience** — tries UTF-8, UTF-8 BOM, latin-1, and CP1252 before giving up
- **File-size limits** — skips files larger than a configurable threshold (default 1 MB)
- **Include/exclude patterns** — glob-based filtering via CLI, env vars, or `.ctxrc` config file
- **Stdin mode** — pipe a file list directly into ctx
- **Self-test** — `ctx --test` runs a comprehensive test suite
- **Zero dependencies** — pure Python stdlib, installs and runs instantly
- **Graceful handling** — SIGINT handler, permission errors skipped with warnings, encoding fallbacks everywhere

## Quick Start

### Using pip

```bash
pip install ctx
ctx .
```

### From Source

```bash
git clone https://github.com/zwart04/ctx.git
cd ctx
pip install -e .
ctx .
```

### Without Installing

```bash
git clone https://github.com/zwart04/ctx.git
cd ctx
python3 -m ctx .
```

## Usage

### Basic

```bash
# Extract current directory as Markdown
python3 -m ctx .

# Extract a specific path
python3 -m ctx src/

# JSON output for scripting
python3 -m ctx . --format json
```

### Filtering

```bash
# Only Python and TypeScript files
python3 -m ctx . --include "*.py" "*.ts"

# Exclude test files
python3 -m ctx . --exclude "test_*" "tests/"

# Ignore .gitignore and include everything
python3 -m ctx . --no-ignore
```

### Advanced

```bash
# Read file list from stdin
find . -name "*.py" | python3 -m ctx . --stdin

# Limit depth and file size
python3 -m ctx . --max-depth 3 --max-file-size 524288

# Omit the directory tree
python3 -m ctx . --no-tree

# Exact token count for GPT-4 (requires tiktoken)
pip install tiktoken 2>/dev/null
python3 -m ctx . --model gpt-4
```

### Pipe to clipboard

```bash
# macOS
python3 -m ctx . | pbcopy

# Linux (xclip)
python3 -m ctx . | xclip -selection clipboard

# Windows (PowerShell)
python3 -m ctx . | Set-Clipboard
```

### Python API

```python
from ctx import extract

# Basic usage
result = extract(".", include=["*.py"])
print(result.content)

# Access structured data
for file in result.files:
    print(f"{file.path}: {file.lines} lines")

# Token metadata
print(f"Tokens: {result.tokens.total} ({result.tokens.method})")
print(f"Chars: {result.tokens.characters}")
print(f"Words: {result.tokens.words}")
```

## Output Examples

### Markdown (default)

~~~markdown
## Directory Structure

```
ctx/
  src/
    __init__.py
    cli.py
    config.py
```

## Files

### src/cli.py

```python
"""Command-line entry point for ctx."""
...
```
~~~

### Plain

```
Directory Structure:
ctx/
  src/
    cli.py
    config.py

src/cli.py
---
"""Command-line entry point for ctx."""
---
```

### JSON

```json
{
  "files": [
    {
      "path": "src/cli.py",
      "content": "'''Command-line entry point for ctx.'''\n...",
      "size": 11520,
      "lines": 240,
      "encoding": "utf-8"
    }
  ]
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CTX_INCLUDE` | Comma/space-separated include globs | — |
| `CTX_EXCLUDE` | Comma/space-separated exclude globs | (built-in defaults) |
| `CTX_MAX_DEPTH` | Maximum directory recursion depth | 5 |
| `CTX_MAX_FILE_SIZE` | Maximum file size in bytes | 1048576 |
| `CTX_NO_IGNORE` | Set to `1` or `true` to ignore .gitignore | — |

### RC File (`.ctxrc` or `ctx.rc`)

Place a `.ctxrc` file in your project root:

```ini
# ctx configuration
INCLUDE = *.py *.ts
EXCLUDE = test_* build/
MAX_DEPTH = 4
NO_IGNORE = 0
```

CLI arguments override environment variables, which override RC file
values, which override built-in defaults.

### Built-in Default Skip Patterns

Files and directories matching these are always excluded (unless
`--no-ignore` is set):

```
.git, node_modules, __pycache__, .venv, venv, .env,
*.pyc, *.egg-info, .DS_Store
```

## Default Skip Patterns

| Pattern | Reason |
|---------|--------|
| `.git/` | Git internals (not useful as context) |
| `node_modules/` | Dependency bloat |
| `__pycache__/` | Python bytecode cache |
| `.venv/`, `venv/` | Virtual environments |
| `.env` | Credentials and secrets |
| `*.pyc`, `*.egg-info` | Build artifacts |
| `.DS_Store` | macOS metadata |

## Architecture

```
ctx/
  src/
    __init__.py     # Public API: extract()
    __main__.py     # python3 -m ctx entry point
    cli.py          # CLI argument parsing + orchestration
    config.py       # Config loader (env vars + .ctxrc)
    scanner.py      # File tree scanner with .gitignore awareness
    reader.py       # File content reader (binary detection + encoding)
    formatter.py    # Output formatters (markdown, plain, json)
    counter.py      # Token counter (estimate + optional tiktoken)
    filters.py      # Gitignore pattern parsing + file filtering
    types.py        # Dataclasses: FileEntry, FileContent, TokenCount, etc.
```

The data flows through a clean pipeline:

```
[Config] → [Scanner] → [Reader] → [Formatter] → [Output]
                              ↘ [Counter] ↙
```

Each stage is a separate module with a single responsibility. Adding a
new output format means adding one function to `formatter.py`. Adding
a new filter means adding a method to `filters.py`.

## Design Philosophy

1. **Zero friction** — Install and run in under 5 seconds. No
   dependencies, no configuration file required, no daemon.

2. **AI-native output** — Markdown with fenced code blocks is the
   format AI coding assistants understand best. Every file gets its own
   heading and code fence for clear delineation.

3. **Graceful by default** — Binary files, permission errors,
   unreadable files, and encoding issues are all handled silently (with
   warnings to stderr). The pipeline never crashes mid-extraction.

4. **Configurable but not demanding** — Sensible defaults work out of
   the box. When you need customisation, CLI flags, env vars, and RC
   files are all supported in ascending priority order.

5. **Dual interface** — CLI for quick extraction, Python API for
   programmatic use. The same code powers both.

## License

MIT
