#!/usr/bin/env bash
# envdoctor Self-Test Script
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PASS=0
FAIL=0

green() { echo -e "\033[92m$1\033[0m"; }
red()   { echo -e "\033[91m$1\033[0m"; }
bold()  { echo -e "\033[1m$1\033[0m"; }

# Use pre-increment to avoid set -e issues with ((var++)) returning 1 when var=0
pass() { PASS=$((PASS + 1)); green "PASS"; }
fail() { FAIL=$((FAIL + 1)); red "FAIL"; }

CMD="python3 -m envdoctor"
cd "$PROJECT_DIR"

bold "=== envdoctor Self-Test Suite ==="
echo ""

# Test 1: --help
echo -n "  [1] --help works ... "
if $CMD --help > /dev/null 2>&1; then pass; else fail; fi

# Test 2: --version
echo -n "  [2] --version shows version ... "
VERSION=$($CMD --version 2>&1)
if echo "$VERSION" | grep -q "envdoctor v"; then pass; else fail; fi

# Test 3: --test (self-test)
echo -n "  [3] --test suite passes ... "
if $CMD --test 2>&1; then pass; else fail; fi

# Test 4: Scan this project (envdoctor scanning itself)
echo -n "  [4] Self-scan produces output ... "
OUTPUT=$($CMD "$PROJECT_DIR" --no-color 2>&1)
if echo "$OUTPUT" | grep -q "envdoctor"; then pass; else fail; fi

# Test 5: JSON output is valid
echo -n "  [5] JSON output is valid ... "
JSON_OUT=$($CMD "$PROJECT_DIR" --json --no-color 2>&1)
if echo "$JSON_OUT" | python3 -c "import json,sys; json.loads(sys.stdin.read())" 2>/dev/null; then pass; else fail; fi

# Test 6: Markdown output
echo -n "  [6] Markdown output is valid ... "
MD_OUT=$($CMD "$PROJECT_DIR" --markdown --no-color 2>&1)
if echo "$MD_OUT" | grep -q "^# Environment Variable Report"; then pass; else fail; fi

# Test 7: Error handling for non-existent path
echo -n "  [7] Handle non-existent path ... "
if $CMD /nonexistent/path --no-color 2>&1 | grep -q "Error"; then pass; else fail; fi

# Test 8: Verify module imports
echo -n "  [8] All modules import cleanly ... "
if python3 -c "from envdoctor import types, scanner, parser, analyzer, reporter, fixer, cli; print('OK')" 2>/dev/null; then pass; else fail; fi

# Test 9: Health score is numeric in JSON
echo -n "  [9] Health score is numeric ... "
HEALTH=$(echo "$JSON_OUT" | python3 -c "import json,sys; d=json.loads(sys.stdin.read()); print(d['summary']['health_score'])")
if echo "$HEALTH" | grep -qE '^[0-9]+(\.[0-9]+)?$'; then pass; else fail; fi

# Test 10: --fix generates .env.example
echo -n "  [10] --fix generates .env.example ... "
TMPDIR=$(mktemp -d)
mkdir -p "$TMPDIR/testproj"
echo 'import os; x = os.environ.get("MY_TEST_VAR")' > "$TMPDIR/testproj/main.py"
PYTHONPATH="$PROJECT_DIR" $CMD "$TMPDIR/testproj" --fix --no-color > /dev/null 2>&1 || true
if [ -f "$TMPDIR/testproj/.env.example" ] && grep -q "MY_TEST_VAR" "$TMPDIR/testproj/.env.example"; then
    rm -rf "$TMPDIR"; pass
else
    rm -rf "$TMPDIR"; fail
fi

# Test 11: Secret detection
echo -n "  [11] Secret detection finds hardcoded tokens ... "
TMPDIR=$(mktemp -d)
echo 'API_KEY="sk-1...f"' > "$TMPDIR/config.py"
OUT=$(PYTHONPATH="$PROJECT_DIR" $CMD "$TMPDIR" --no-color 2>&1)
if echo "$OUT" | grep -qi "secret"; then
    rm -rf "$TMPDIR"; pass
else
    rm -rf "$TMPDIR"; fail
fi

echo ""
bold "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
