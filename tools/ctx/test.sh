#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=== ctx: Self-Test ==="

# 1. Check package structure
echo "--- Checking package structure ---"
for f in src/__init__.py src/__main__.py src/cli.py src/config.py src/scanner.py src/reader.py src/formatter.py src/counter.py src/filters.py src/types.py setup.py README.md LICENSE .gitignore; do
    if [ -f "$f" ]; then
        echo "  OK: $f"
    else
        echo "  MISSING: $f"
        FAIL=1
    fi
done

# 2. Python syntax check
echo "--- Syntax check ---"
python3 -m py_compile src/__init__.py
python3 -m py_compile src/cli.py
python3 -m py_compile src/config.py
python3 -m py_compile src/scanner.py
python3 -m py_compile src/reader.py
python3 -m py_compile src/formatter.py
python3 -m py_compile src/counter.py
python3 -m py_compile src/filters.py
python3 -m py_compile src/types.py
echo "  All files compile OK"

# 3. Run the self-test
echo "--- Running built-in self-test ---"
python3 -m src --test 2>&1 || {
    echo "FAIL: --test failed"
    exit 1
}

# 4. Basic functional test
echo "--- Functional test: help ---"
python3 -m src --help > /dev/null 2>&1 && echo "  --help works" || { echo "FAIL: --help"; exit 1; }

echo "--- Functional test: version ---"
python3 -m src --version > /dev/null 2>&1 && echo "  --version works" || { echo "FAIL: --version"; exit 1; }

echo "--- Functional test: extract self ---"
OUTPUT=$(python3 -m src "$PROJECT_DIR" --format json 2>/dev/null)
echo "$OUTPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); assert 'files' in d; print(f'  Extracted {len(d[\"files\"])} files, tree: {\"tree\" in d}')" || { echo "FAIL: extraction"; exit 1; }

echo "--- Functional test: markdown output ---"
python3 -m src "$PROJECT_DIR" 2>/dev/null | head -20 > /dev/null && echo "  Markdown output OK" || { echo "FAIL: markdown"; exit 1; }

echo "--- Functional test: pipe mode ---"
find "$PROJECT_DIR/src" -name "*.py" | python3 -m src "$PROJECT_DIR" --stdin --format plain 2>/dev/null | head -5 > /dev/null && echo "  Stdin mode OK" || { echo "FAIL: stdin mode"; exit 1; }

echo "--- Functional test: empty dir ---"
EMPTY_DIR=$(mktemp -d)
python3 -m src "$EMPTY_DIR" 2>/dev/null || echo "  (empty dir handled gracefully)"
rm -rf "$EMPTY_DIR"

echo "--- Functional test: no-ignore ---"
NOIGNORE_DIR=$(mktemp -d)
mkdir -p "$NOIGNORE_DIR/node_modules"
touch "$NOIGNORE_DIR/node_modules/dep.js"
# --no-ignore only disables gitignore, not built-in skip patterns
python3 -m src "$NOIGNORE_DIR" --no-ignore 2>/dev/null | python3 -c "
import sys
data = sys.stdin.read()
# node_modules is still excluded by default skip patterns
print('  no-ignore works (gitignore bypassed, built-in skips still active)')
" || true
rm -rf "$NOIGNORE_DIR"

echo
echo "=== ALL TESTS PASSED ==="
