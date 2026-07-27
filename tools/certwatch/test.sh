#!/usr/bin/env bash
set -euo pipefail

# certwatch — self-test script

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PASS=0
FAIL=0

green() { printf '\033[32m%s\033[0m\n' "$1"; }
red()   { printf '\033[31m%s\033[0m\n' "$1"; }

check() {
    local desc="$1"
    shift
    if "$@" 2>&1; then
        green "  PASS: $desc"
        PASS=$((PASS + 1))
    else
        red "  FAIL: $desc"
        FAIL=$((FAIL + 1))
    fi
}

echo ""
echo "=== certwatch test suite ==="
echo ""

# 1. Self-test
check "built-in self-test" python3 -m certwatch.cli --test

# 2. --help
check "--help works" python3 -m certwatch.cli --help

# 3. --version check (via __init__)
check "version attribute" python3 -c "from certwatch import __version__; assert __version__ == '1.0.0'"

# 4. Parse targets test
check "parse_targets module" python3 -c "
from certwatch.checker import parse_targets
t = parse_targets(['example.com', 'google.com:8443'])
assert len(t) == 2
assert t[0] == ('example.com', 443)
assert t[1] == ('google.com', 8443)
print('OK')
"

# 5. Types test
check "types module" python3 -c "
from certwatch.types import CertInfo, CheckResult
from datetime import datetime, timezone, timedelta
ci = CertInfo(hostname='t.com', port=443, status='valid',
    not_before=datetime.now(timezone.utc) - timedelta(days=30),
    not_after=datetime.now(timezone.utc) + timedelta(days=60))
assert ci.is_valid
assert not ci.is_expired
cr = CheckResult()
cr.results = [ci, CertInfo(hostname='e.com', port=443, status='error', error='err')]
cr.aggregate()
assert cr.valid_count == 1
assert cr.error_count == 1
print('OK')
"

# 6. Config test
check "config module" python3 -c "
from certwatch.config import Config
c = Config(warn_days=30, crit_days=7, timeout_seconds=10, max_concurrent=50, verbose=False)
errs = c.validate()
assert not errs, f'Unexpected errors: {errs}'
c2 = Config(warn_days=7, crit_days=30, timeout_seconds=10, max_concurrent=50, verbose=False)
errs2 = c2.validate()
assert len(errs2) > 0, 'Should fail: crit > warn'
print('OK')
"

# 7. Output module imports
check "output module imports" python3 -c "
from certwatch.output import output_json, output_table, output_summary, output_nagios
print('OK')
"

# 8. Package install
check "pip install" python3 -m pip install -e . --quiet 2>&1

# 9. CLI entry point
check "certwatch command exists" command -v certwatch

# 10. Real SSL check (no pipe - save to temp file)
echo "  Running SSL check against example.com..."
set +e
certwatch --json example.com 2>/dev/null > /tmp/certwatch_test.json
CERTWATCH_EXIT=$?
set -e
if [ $CERTWATCH_EXIT -eq 0 ] && python3 -c "
import json
with open('/tmp/certwatch_test.json') as f:
    data = json.load(f)
assert 'results' in data
assert len(data['results']) > 0
r = data['results'][0]
assert r['hostname'] == 'example.com'
assert r['status'] in ('valid', 'warning', 'critical')
assert r['days_remaining'] is not None
print('OK: ' + r['hostname'] + ' ' + str(r['status']) + ' ' + str(r['days_remaining']) + 'd')
"; then
    green "  PASS: SSL check example.com"
    PASS=$((PASS + 1))
else
    red "  FAIL: SSL check example.com"
    FAIL=$((FAIL + 1))
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
