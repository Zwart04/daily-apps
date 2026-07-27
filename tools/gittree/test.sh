#!/usr/bin/env bash
set -e

PROJ_DIR="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$PROJ_DIR/src:$PYTHONPATH"

echo "=== gittree Self-Test ==="

# Test 1: --help
echo "--- Test: --help ---"
python3 -m gittree --help > /dev/null && echo "PASS: --help works" || echo "FAIL: --help"

# Test 2: --version
echo "--- Test: --version ---"
python3 -m gittree --version 2>&1 | grep -q "gittree" && echo "PASS: --version works" || echo "FAIL: --version"

# Test 3: --test (self-test suite)
echo "--- Test: --test ---"
python3 -m gittree --test 2>&1 | tail -3 && echo "PASS: self-test passed" || (echo "FAIL: self-test"; exit 1)

# Test 4: Scan a known directory
echo "--- Test: status on /root ---"
python3 -m gittree status /root --depth 2 --format json > /tmp/gittree-test.json
python3 -c "
import json
with open('/tmp/gittree-test.json') as f:
    data = json.load(f)
assert 'repos' in data, 'Missing repos key'
assert 'summary' in data, 'Missing summary key'
assert data['summary']['total'] > 0, 'Expected at least 1 repo'
print(f'PASS: Found {data[\"summary\"][\"total\"]} repos under /root')
print(f'     {data[\"summary\"][\"clean\"]} clean, {data[\"summary\"][\"dirty\"]} dirty, {data[\"summary\"][\"ahead\"]} ahead')
"

# Test 5: Scan non-existent directory (should output valid JSON with 0 repos)
echo "--- Test: status on /nonexistent ---"
python3 -m gittree status /nonexistent --format json > /tmp/gittree-empty.json
python3 -c "
import json
with open('/tmp/gittree-empty.json') as f:
    data = json.load(f)
assert len(data['repos']) == 0, 'Expected 0 repos'
assert data['summary']['total'] == 0, 'Expected summary total 0'
print('PASS: Valid JSON with 0 repos for nonexistent directory')
"

# Test 6: summary command
echo "--- Test: summary ---"
python3 -m gittree summary /root --depth 2 > /dev/null && echo "PASS: summary works" || echo "FAIL: summary"

# Test 7: dirty filter
echo "--- Test: dirty ---"
python3 -m gittree dirty /root --depth 2 --format json > /tmp/gittree-dirty.json
python3 -c "
import json
with open('/tmp/gittree-dirty.json') as f:
    data = json.load(f)
print(f'PASS: dirty filter found {len(data[\"repos\"])} repos with changes')
"

# Test 8: Color terminal output (non-JSON)
echo "--- Test: color terminal output ---"
python3 -m gittree status /root --depth 2 > /dev/null && echo "PASS: color output works" || echo "FAIL: color output"

# Test 9: ahead filter
echo "--- Test: ahead ---"
python3 -m gittree ahead /root --depth 2 --format json > /tmp/gittree-ahead.json
python3 -c "
import json
with open('/tmp/gittree-ahead.json') as f:
    data = json.load(f)
print(f'PASS: ahead filter works ({len(data[\"repos\"])} repos)')
"

# Test 10: Invoke via wrapper script
echo "--- Test: wrapper script ---"
$PROJ_DIR/gittree --version > /dev/null && echo "PASS: wrapper script works" || echo "FAIL: wrapper script"

echo ""
echo "=== All tests passed ==="
